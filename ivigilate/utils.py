from datetime import datetime, timezone, timedelta
import threading
import pytz
import requests
from rest_framework.response import Response
from rest_framework import status
from twilio.rest import TwilioRestClient
from django.core.mail import send_mail
from ivigilate import settings
from ivigilate.serializers import SightingReadSerializer
from ivigilate.models import Sighting, Event, EventOccurrence, Notification, Limit, LimitOccurrence
from django.db.models import Q
import math, json, re, logging, os

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def view_list(request, account, queryset, serializer):
    if account is None or account.get_license_in_force() is not None:
        serializer_response = serializer(queryset, many=True, context={'request': request})
        # page = self.paginate_queryset(queryset)
        # serializer = self.get_pagination_serializer(page)

        responseObject = {'timestamp': datetime.now(timezone.utc),
                         'list': serializer_response.data} \
            if issubclass(serializer, SightingReadSerializer) else \
            serializer_response.data
        return Response(responseObject)
    else:
        return Response('Your license has expired. Please ask the account administrator to renew the subscription.',
                        status=status.HTTP_401_UNAUTHORIZED)


def get_file_extension(file_name, decoded_file):
    import imghdr

    extension = imghdr.what(file_name, decoded_file)
    extension = "jpg" if extension == "jpeg" else extension

    return extension


def replace_tags(msg, event=None, beacon=None, detector=None, limit=None):
    return msg.replace('%event_id%', event.reference_id if event is not None else ''). \
        replace('%event_name%', event.name if event is not None else ''). \
        replace('%beacon_id%', beacon.reference_id if beacon is not None else ''). \
        replace('%beacon_name%', beacon.name if beacon is not None else ''). \
        replace('%detector_id%', detector.reference_id if detector is not None else ''). \
        replace('%detector_name%', detector.name if detector is not None else ''). \
        replace('%limit_id%', limit.reference_id if limit is not None else ''). \
        replace('%limit_name%', limit.name if limit is not None else '')


def send_twilio_message(to, msg):
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=msg,
        to=to,
        from_=settings.TWILIO_DEFAULT_CALLERID,
    )


def make_rest_call(method, uri, body):
    if method == 'GET':
        requests.get(uri, body)
    elif method == 'POST':
        requests.post(uri, body)
    elif method == 'PUT':
        requests.put(uri, body)


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
            perform_action(action, event, sighting.beacon, sighting.detector, None)


def trigger_limit_actions(limit, event, beacon):
    logger.info('Conditions met for limit \'%s\'. Triggering corresponding actions...', limit)
    limit_occurrence = LimitOccurrence.objects.create(limit=limit, event=event, beacon=beacon)

    metadata = json.loads(limit.metadata)
    actions = metadata['actions']
    if actions:
        for action in actions:
            perform_action(action, event, beacon, None, limit)


def perform_action(action, event, beacon, detector, limit):
    try:
        if action['type'] == 'NOTIFICATION':
            logger.info('Action for ' + ('event' if event is not None else 'limit') + ' \'%s\': Generating On-Screen Notification.',
                        event if event is not None else limit)
            action_metadata = {}
            action_metadata['category'] = action['category']
            action_metadata['timeout'] = action.get('timeout', 0)
            action_metadata['title'] = replace_tags(action.get('title', ''), event, beacon, detector, limit)
            action_metadata['message'] = replace_tags(action.get('message', ''), event, beacon, detector, limit)
            Notification.objects.create(account=event.account, metadata=json.dumps(action_metadata))
        elif action['type'] == 'SMS':
            logger.info('Action for ' + ('event' if event is not None else 'limit') + ' \'%s\': Sending SMS to %s recipient(s).',
                    event if event is not None else limit, len(re.split(',|;', action['recipients'])))
            message = replace_tags(action.get('message', ''), event, beacon, detector, limit)
            for to in re.split(',|;', action['recipients']):
                send_twilio_message(to, message)
        elif action['type'] == 'EMAIL':
            logger.info('Action for ' + ('event' if event is not None else 'limit') + ' \'%s\': Sending EMAIL to %s recipient(s).',
                    event if event is not None else limit, len(re.split(',|;', action['recipients'])))
            body = replace_tags(action.get('body', ''), event, beacon, detector, limit)
            subject = replace_tags(action.get('subject', ''), event, beacon, detector, limit)
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                    re.split(',|;', action['recipients']), fail_silently=False)
        elif action['type'] == 'REST':
            uri = replace_tags(action['uri'], event, beacon, detector, limit)
            logger.info('Action for ' + ('event' if event is not None else 'limit') + ' \'%s\': Making a \'%s\' call to \'%s\'.',
                    event if event is not None else limit, action['method'], uri)
            body = replace_tags(action.get('body', ''), event, beacon, detector, limit)
            make_rest_call(action['method'], uri, body)
    except Exception as ex:
        logger.exception('Failed to perform action of type \'%s\':', action['type'])


def check_for_events_async(sighting, new_sighting_detector=None):
    # check for events associated with this sighting in a different  thread
    t = threading.Thread(target=check_for_events, args=(sighting, new_sighting_detector))
    t.start()


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
            conditions_met = False
            event_metadata = json.loads(event.metadata)
            sighting_metadata = json.loads(sighting.metadata or '{}')
            initial_timestamp = sighting_metadata.get('timestamp_event_id_' + str(event.id), None)

            # Check if the bulk of the conditions are met...
            if (event_metadata.get('sighting_is_current', None) is None or
                        event_metadata['sighting_is_current'] == sighting.is_current) and \
                            event_metadata.get('sighting_has_battery_below', 0) >= sighting.battery and \
                    (event_metadata.get('sighting_has_comment', None) is None or
                         (event_metadata['sighting_has_comment'] and sighting.comment) or
                         (not event_metadata['sighting_has_comment'] and not sighting.comment)) and \
                    (event_metadata.get('sighting_has_been_confirmed', None) is None or
                         (event_metadata['sighting_has_been_confirmed'] and sighting.confirmed) or
                         (not event_metadata['sighting_has_been_confirmed'] and not sighting.confirmed)) and \
                    (event_metadata.get('sighting_arrival_rssi', 0) >= sighting.rssi and
                         (event_metadata.get('sighting_departure_rssi', -99) < sighting.rssi)) and \
                    (new_sighting_detector is None or len(event.detectors.all()) == 0 or new_sighting_detector in event.detectors.all()):

                # Check the sighting duration within the proximity range specified in the event
                event_sighting_duration_in_seconds = event_metadata.get('sighting_duration_in_seconds', 0)
                if event_sighting_duration_in_seconds > 0:
                    if initial_timestamp is not None:
                        if (sighting.last_seen_at - datetime.fromtimestamp(initial_timestamp).replace(tzinfo=timezone.utc)).total_seconds() >= event_sighting_duration_in_seconds:
                            conditions_met = True
                    else:
                        sighting_metadata['timestamp_event_id_' + str(event.id)] = sighting.last_seen_at.replace(tzinfo=timezone.utc).timestamp()
                        sighting.metadata = json.dumps(sighting_metadata)
                        sighting.save()
                else:
                    conditions_met = True

            elif initial_timestamp is not None:
                sighting_metadata['timestamp_event_id_' + str(event.id)] = None
                sighting.metadata = json.dumps(sighting_metadata)
                sighting.save()


            if conditions_met:
                if (event_metadata.get('sighting_previous_event', None) is None):
                    # Make sure we don't trigger the same actions over and over again (only once per sighting)
                    same_occurrence_count = EventOccurrence.objects.filter(event=event, sighting=sighting).count()
                    if (same_occurrence_count == 0):
                        previous_occurrences = EventOccurrence.objects.filter(event=event,
                                                                              sighting__beacon=sighting.beacon,
                                                                              sighting__detector=sighting.detector
                                                                            ).order_by('-id')[:1]
                        if (event_metadata.get('sighting_dormant_period_in_seconds', None) is None or
                                event_metadata['sighting_dormant_period_in_seconds'] <= 0 or
                                previous_occurrences is None or len(previous_occurrences) == 0 or
                                now - timedelta(seconds=event_metadata['sighting_dormant_period_in_seconds']) > previous_occurrences[0].occurred_at):
                            trigger_event_actions(event, sighting)
                        else:
                            logger.debug('Conditions met for event \'%s\' but skipping it has ' + \
                                         'the tuple event / beacon / detector is still in the dormant period.', event)
                    else:
                        logger.debug('Conditions met for event \'%s\' ' + \
                                     'but the required actions were already triggered once for this sighting.', event)
                else:  # event conditions require that a specific previous event had occurred
                    previous_occurrences = EventOccurrence.objects.filter(sighting__beacon=sighting.beacon).order_by('-id')[:2]
                    if (previous_occurrences is not None and len(previous_occurrences) > 0 and
                                previous_occurrences[0].event_id == event_metadata['sighting_previous_event']['id']):
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

    limits = Limit.objects.filter(Q(is_active=True),
                                        Q(events=None)|Q(events__id__exact=event_occurrence.event.id),
                                        Q(beacons=None)|Q(beacons__id__exact=event_occurrence.sighting.beacon.id),
                                        Q(start_date__lte=event_occurrence.occurred_at)
                                        ).order_by('-start_date')[:1]

    if limits:
        logger.debug('Found %s limit(s) active for event_occurrence \'%s\'.', len(limits), event_occurrence)
        for limit in limits:
            logger.debug('Checking if \'%s\' limit conditions are met...', limit)
            metadata = json.loads(limit.metadata)
            filter_date_limit = datetime.strptime(metadata['occurrence_date_limit'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC) + timedelta(days=1) if metadata.get('occurrence_date_limit', None) is not None else None
            if (metadata.get('occurrence_date_limit', None) is not None and
                        event_occurrence.occurred_at >= filter_date_limit):
                logger.info('Conditions met for limit \'%s\' with event occurrence \'%s\' due to going over the date limit.', limit, event_occurrence)
                trigger_limit_actions(limit, event_occurrence.event, event_occurrence.sighting.beacon)
            elif (metadata['occurrence_count_limit'] >= 0):
                eos = EventOccurrence.objects.all()
                if (metadata.get('occurrence_date_limit', None) is not None):
                    eos = eos.filter(event=event_occurrence.event,
                                     occurred_at__gte=limit.start_date,
                                     occurred_at__lt=filter_date_limit)
                else:
                    eos = eos.filter(event=event_occurrence.event,
                                     occurred_at__gte=limit.start_date)

                if (metadata['consider_each_beacon_separately']):
                    eos = eos.filter(sighting__beacon=event_occurrence.sighting.beacon)
                elif (limit.beacons and limit.beacons.count() > 0):
                    eos = eos.filter(sighting__beacon__in=limit.beacons.all())

                if (eos.count() > metadata['occurrence_count_limit']):
                    logger.debug('Conditions met for limit \'%s\' with event occurrence \'%s\' due to going over the count limit.', len(limits), event_occurrence)
                    trigger_limit_actions(limit, event_occurrence.event, event_occurrence.sighting.beacon)
                else:
                    logger.info('Conditions not met for limit \'%s\'. ', limit)
            else:
                logger.info('Conditions not met for limit \'%s\'. ', limit)