from datetime import datetime, timezone, timedelta
import threading
from rest_framework.response import Response
from rest_framework import status
from twilio.rest import TwilioRestClient
from django.core.mail import send_mail
from ivigilate import settings
from ivigilate.models import Sighting, Event, EventOccurrence, Notification, EventLimit
from django.db.models import Q
import math, json, re, logging, os

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def view_list(request, account, queryset, serializer):
    if account is None or account.get_license_in_force() is not None:
        serializer_response = serializer(queryset, many=True, context={'request': request})
        # page = self.paginate_queryset(queryset)
        # serializer = self.get_pagination_serializer(page)
        return Response(serializer_response.data)
    else:
        return Response('Your license has expired. Please ask the account administrator to renew the subscription.',
                        status=status.HTTP_401_UNAUTHORIZED)


def get_file_extension(file_name, decoded_file):
    import imghdr

    extension = imghdr.what(file_name, decoded_file)
    extension = "jpg" if extension == "jpeg" else extension

    return extension


def replace_event_message_tags(msg, event, sighting):
    return msg.replace('%event_id%', event.reference_id). \
        replace('%event_name%', event.name). \
        replace('%beacon_id%', sighting.beacon.reference_id). \
        replace('%beacon_name%', sighting.beacon.name). \
        replace('%detector_id%', sighting.detector.reference_id). \
        replace('%detector_name%', sighting.detector.name)


def replace_limit_message_tags(msg, limit, beacon):
    return msg.replace('%limit_id%', limit.reference_id). \
        replace('%event_id%', limit.event.reference_id). \
        replace('%event_name%', limit.event.name). \
        replace('%beacon_id%', beacon.reference_id). \
        replace('%beacon_name%', beacon.name)

def send_twilio_message(to, msg):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID', 'AC1b8158faf55b96ed86dee884e1d94beb' if settings.DEBUG else None)
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '3941cff26f237a3540627a5f52ca6e85' if settings.DEBUG else None)
    caller_id = os.environ.get('TWILIO_DEFAULT_CALLERID', '14158438604' if settings.DEBUG else None)

    client = TwilioRestClient(account_sid, auth_token)
    message = client.messages.create(
        body=msg,
        to=to,
        from_=caller_id,
    )


def close_sighting(sighting, new_sighting_detector=None):
    sighting.is_current = False
    sighting.save()
    logger.debug('Sighting \'%s\' is no longer current.', sighting)

    # check for events associated with this sighting in a different thread
    t = threading.Thread(target=check_for_events, args=(sighting, new_sighting_detector,))
    t.start()


def trigger_event_actions(event, sighting):
    logger.info('Conditions met for event \'%s\'. Creating EventOccurrence and triggering actions...', event)
    event_occurrence = EventOccurrence.objects.create(event=event, sighting=sighting)

    # check for events associated with this sighting in a different thread
    t = threading.Thread(target=check_for_limits, args=(event_occurrence,))
    t.start()

    metadata = json.loads(event.metadata)
    actions = metadata['actions']
    if actions:
        for action in actions:
            if action['type'] == 'NOTIFICATION':
                logger.info('Action for event \'%s\': Generating On-Screen Notification.', event)
                action_metadata = {}
                action_metadata['category'] = action['category']
                action_metadata['timeout'] = action.get('timeout', 0)
                action_metadata['title'] = replace_event_message_tags(action.get('title', ''), event, sighting)
                action_metadata['message'] = replace_event_message_tags(action.get('message', ''), event, sighting)
                Notification.objects.create(account=event.account, metadata=json.dumps(action_metadata))
            elif action['type'] == 'SMS':
                logger.info('Action for event \'%s\': Sending SMS to %s recipient(s).',
                             event, len(re.split(',|;', action['recipients'])))
                message = replace_event_message_tags(action.get('message', ''), event, sighting)
                for to in re.split(',|;', action['recipients']):
                    send_twilio_message(to, message)
            elif action['type'] == 'EMAIL':
                logger.info('Action for event \'%s\': Sending EMAIL to %s recipient(s).',
                             event, len(re.split(',|;', action['recipients'])))
                body = replace_event_message_tags(action.get('body', ''), event, sighting)
                subject = replace_event_message_tags(action.get('subject', ''), event, sighting)
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                          re.split(',|;', action['recipients']), fail_silently=False)


def trigger_limit_actions(limit, beacon):
    logger.info('Conditions met for limit \'%s\'. Triggering corresponding actions...', limit)

    metadata = json.loads(limit.metadata)
    actions = metadata['actions']
    if actions:
        for action in actions:
            if action['type'] == 'NOTIFICATION':
                logger.info('Action for limit \'%s\': Generating On-Screen Notification.', limit)
                action_metadata = {}
                action_metadata['category'] = action['category']
                action_metadata['timeout'] = action.get('timeout', 0)
                action_metadata['title'] = replace_limit_message_tags(action.get('title', ''), limit, beacon)
                action_metadata['message'] = replace_limit_message_tags(action.get('message', ''), limit, beacon)
                Notification.objects.create(account=limit.event.account, metadata=json.dumps(action_metadata))
            elif action['type'] == 'SMS':
                logger.info('Action for limit \'%s\': Sending SMS to %s recipient(s).',
                             limit, len(re.split(',|;', action['recipients'])))
                message = replace_limit_message_tags(action.get('message', ''), limit, beacon)
                for to in re.split(',|;', action['recipients']):
                    send_twilio_message(to, message)
            elif action['type'] == 'EMAIL':
                logger.info('Action for event \'%s\': Sending EMAIL to %s recipient(s).',
                             limit, len(re.split(',|;', action['recipients'])))
                body = replace_limit_message_tags(action.get('body', ''), limit, beacon)
                subject = replace_limit_message_tags(action.get('subject', ''), limit, beacon)
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                          re.split(',|;', action['recipients']), fail_silently=False)


def check_for_events(sighting, new_sighting_detector=None):
    logger.debug('Checking for events associated with sighting \'%s\'...', sighting)
    now = datetime.now(timezone.utc)
    current_week_day_representation = math.pow(2, now.weekday())

    raw_query = Event.objects.raw('SELECT e.* ' + \
                                  'FROM ivigilate_event e ' \
                                  'LEFT OUTER JOIN ivigilate_event_beacons eb ON e.id = eb.event_id ' \
                                  'LEFT OUTER JOIN ivigilate_event_detectors ed ON e.id = ed.event_id ' \
                                  'WHERE (e.is_active = True ' \
                                  'AND (eb.beacon_id IS NULL OR eb.beacon_id = %s) ' \
                                  'AND (ed.detector_id IS NULL OR ed.detector_id = %s) ' \
                                  'AND e.schedule_days_of_week & %s > 0 ' \
                                  'AND e.schedule_start_time <= (%s + interval \'1m\' * e.schedule_timezone_offset) :: time ' \
                                  'AND e.schedule_end_time >= (%s + interval \'1m\' * e.schedule_timezone_offset) :: time)',
                                  [sighting.beacon.id, sighting.detector.id if sighting.detector is not None else 0,
                                   int(current_week_day_representation),
                                   now.strftime('%H:%M:%S'), now.strftime('%H:%M:%S')])

    # To use the ORM version below, need to move timezone_offset field to Account model or Detector model
    # filter_date = now + timedelta(minutes=sighting.place.account.timezone_offset)
    #events = Event.objects.filter(Q(is_active=True),
    #                              Q(movables=None)|Q(movables__id__exact=sighting.movable.id),
    #                              Q(places=None)|Q(places__id__exact=sighting.place.id),
    #                              Q(schedule_days_of_week__bwand=current_week_day_representation),
    #                              Q(schedule_start_time__lte=filter_date),
    #                              Q(schedule_end_time__gte=filter_date))

    # print(raw_query.query)
    events = list(raw_query)
    if events:
        logger.debug('Found %s event(s) active for sighting \'%s\'.', len(events), sighting)
        for event in events:
            logger.debug('Checking if \'%s\' event conditions are met...', event)
            if event.sighting_is_current == sighting.is_current and \
                            event.sighting_has_battery_below >= (sighting.battery or 0) and \
                            event.sighting_duration_in_seconds <= sighting.get_duration() and \
                    ((event.sighting_has_comment is None) or
                         (event.sighting_has_comment and sighting.comment) or
                         (not event.sighting_has_comment and not sighting.comment)) and \
                    ((event.sighting_has_been_confirmed is None) or
                         (event.sighting_has_been_confirmed and sighting.confirmed) or
                         (not event.sighting_has_been_confirmed and not sighting.confirmed)) and \
                    (new_sighting_detector is None or len(event.detectors.all()) == 0 or new_sighting_detector in event.detectors.all()):

                if (event.sighting_previous_event is None):
                    # Make sure we don't trigger the same actions over and over again (only once per sighting)
                    same_occurrence_count = EventOccurrence.objects.filter(event=event, sighting=sighting).count()
                    if (same_occurrence_count == 0):
                        previous_occurrences = EventOccurrence.objects.filter(event=event,
                                                                              sighting__beacon=sighting.beacon,
                                                                              sighting__detector=sighting.detector
                                                                            ).order_by('-id')[:1]
                        if (event.dormant_period_in_seconds <= 0 or
                            previous_occurrences is None or len(previous_occurrences) == 0 or
                            now - timedelta(seconds=event.dormant_period_in_seconds) > previous_occurrences[0].occurred_at):
                            trigger_event_actions(event, sighting)
                        else:
                            logger.debug('Conditions met for event \'%s\' but skipping it has ' + \
                                         'the tuple event / beacon / detector is still in the dormant period.', event)
                    else:
                        logger.debug('Conditions met for event \'%s\' ' + \
                                     'but the required actions were already triggered once for this sighting.', event)
                else:  # event conditions require that a specific previous event had occurred
                    previous_occurrences = EventOccurrence.objects.filter(beacon=sighting.beacon).order_by('-id')[:2]
                    if (previous_occurrences is not None and len(previous_occurrences) > 0 and
                                previous_occurrences[0].event_id == event.sighting_previous_event.id):
                        if (len(previous_occurrences) > 1 and (previous_occurrences[0].sighting_id != sighting.id or
                                    previous_occurrences[1].event_id != event.id)):
                            trigger_event_actions(event, sighting)
                        else:
                            logger.debug('Conditions met for event \'%s\' ' + \
                                     'but the required actions were already triggered once for this sighting.', event)
                    else:
                        logger.info('Conditions not met for event \'%s\'. ' + \
                                    'Previous event occurrence doesn\'t match configured one', event)
            else:
                logger.info('Conditions not met for event \'%s\'. ', event)


def check_for_limits(event_occurrence):
    logger.debug('Checking for limits associated with event_occurrence \'%s\'...', event_occurrence)

    limits = EventLimit.objects.filter(Q(is_active=True),
                                        Q(event=event_occurrence.event),
                                        Q(beacons=None)|Q(beacons__id__exact=event_occurrence.sighting.beacon.id),
                                        Q(occurrence_date_start_limit__lte=event_occurrence.occurred_at)
                                        ).order_by('-occurrence_date_start_limit')[:1]

    if limits:
        logger.debug('Found %s limit(s) active for event_occurrence \'%s\'.', len(limits), event_occurrence)
        for limit in limits:
            filter_date_end_limit = limit.occurrence_date_end_limit + timedelta(days=1) if limit.occurrence_date_end_limit is not None else None
            if (limit.occurrence_date_end_limit is not None and
                        event_occurrence.occurred_at >= filter_date_end_limit):
                logger.debug('Found %s limit(s) active for event_occurrence \'%s\'.', len(limits), event_occurrence)
                trigger_limit_actions(limit, event_occurrence.sighting.beacon)
            elif (limit.occurrence_count_limit >= 0):
                eos = EventOccurrence.objects.all()
                if (limit.occurrence_date_end_limit is not None):
                    eos = eos.filter(event=limit.event,
                                     occurred_at__gte=limit.occurrence_date_start_limit,
                                     occurred_at__lt=filter_date_end_limit)
                else:
                    eos = eos.filter(event=limit.event,
                                     occurred_at__gte=limit.occurrence_date_start_limit)

                metadata = json.loads(limit.metadata)
                if (metadata['consider_each_beacon_separately']):
                    eos = eos.filter(sighting__beacon=event_occurrence.sighting.beacon)
                elif (limit.beacons and limit.beacons.count() > 0):
                    eos = eos.filter(sighting__beacon__in=limit.beacons.all())

                if (eos.count() > limit.occurrence_count_limit):
                    trigger_limit_actions(limit, event_occurrence.sighting.beacon)

