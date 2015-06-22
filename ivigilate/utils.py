from datetime import datetime, timezone, timedelta
from rest_framework.response import Response
from rest_framework import status
from twilio.rest import TwilioRestClient
from django.core.mail import send_mail
from ivigilate import settings
from ivigilate.models import Sighting, Event, EventOccurrence
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


def replace_message_tags(msg, event, sighting):
    return msg.replace('%event_id%', event.reference_id). \
        replace('%event_name%', event.name). \
        replace('%beacon_id%', sighting.beacon.reference_id). \
        replace('%beacon_name%', sighting.beacon.name). \
        replace('%detector_id%', sighting.detector.reference_id). \
        replace('%detector_name%', sighting.detector.name)


def send_twilio_message(to, msg):
    client = TwilioRestClient(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
    message = client.messages.create(
        body=msg,
        to=to,
        from_=os.environ['TWILIO_DEFAULT_CALLERID'],
    )


def close_sighting(sighting, new_sighting_detector=None):
    sighting.is_current = False
    check_for_events(sighting, new_sighting_detector)
    sighting.save()
    logger.debug('Sighting \'%s\' is no longer current.', sighting)


def trigger_event_actions(event, sighting):
    logger.info('Conditions met for event \'%s\'. Creating EventOccurrence and triggering actions...', event)
    EventOccurrence.objects.create(event=event, sighting=sighting, beacon=sighting.beacon)

    metadata = json.loads(event.metadata)
    actions = metadata['actions']
    if actions:
        for action in actions:
            if action['type'] == 'SMS':
                logger.info('Action for event \'%s\': Sending SMS to %s recipient(s).',
                             event, len(re.split(',|;', action['recipients'])))
                message = replace_message_tags(action['message'], event, sighting)
                for to in re.split(',|;', action['recipients']):
                    send_twilio_message(to, message)
            elif action['type'] == 'EMAIL':
                logger.info('Action for event \'%s\': Sending EMAIL to %s recipient(s).',
                             event, len(re.split(',|;', action['recipients'])))
                body = replace_message_tags(action['body'], event, sighting)
                send_mail(action['subject'], body, settings.DEFAULT_FROM_EMAIL,
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
                                  'AND e.schedule_start_time <= %s + interval \'1m\' * e.schedule_timezone_offset ' \
                                  'AND e.schedule_end_time >= %s + interval \'1m\' * e.schedule_timezone_offset)',
                                  [sighting.beacon.id, sighting.detector.id if sighting.detector is not None else 0,
                                   int(current_week_day_representation),
                                   now.strftime('%H:%M:%S'), now.strftime('%H:%M:%S')])

    # To user the ORM version below, need to move timezone_offset field to Account model or Detector model
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
            logger.debug('Checking if \'%s\' event conditions are met.', event)
            if event.sighting_is_current == sighting.is_current and \
                            event.sighting_has_battery_below >= (sighting.battery or 0) and \
                            event.sighting_duration_in_seconds <= sighting.get_duration() and \
                    ((event.sighting_has_comment is None) or
                         (event.sighting_has_comment and sighting.comment) or
                         (not event.sighting_has_comment and not sighting.comment)) and \
                    ((event.sighting_has_been_confirmed is None) or
                         (event.sighting_has_been_confirmed and sighting.confirmed) or
                         (not event.sighting_has_been_confirmed and not sighting.confirmed)) and \
                    (new_sighting_detector is None or new_sighting_detector in event.detectors.all()):

                if (event.sighting_previous_event is None):
                    # Make sure we don't trigger the same actions over and over again (only once per sighting)
                    previous_occurrences = EventOccurrence.objects.filter(event=event, sighting=sighting).order_by('-id')[:1]
                    if (previous_occurrences is None or len(previous_occurrences) == 0):
                        trigger_event_actions(event, sighting)
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



