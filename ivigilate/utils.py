from datetime import datetime, timezone, timedelta
from rest_framework.response import Response
from rest_framework import status
from ivigilate import actions
from ivigilate.serializers import SightingReadSerializer
from ivigilate.models import Sighting, Event, EventOccurrence, Limit, LimitOccurrence
from django.db.models import Q
import math, json, logging, time, threading, pytz

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

TIMESTAMP_DIFF_ALLOWED = 30 * 1000

def build_http_response(response, status):
    return Response({'timestamp': int(time.time() * 1000),  # all ints are long in python 3...
              'data': response},
              status=status)

def view_list(request, account, queryset, serializer, wrap=False):
    if account is None or account.get_license_in_force() is not None:
        serializer_response = serializer(queryset, many=True, context={'request': request})
        # page = self.paginate_queryset(queryset)
        # serializer = self.get_pagination_serializer(page)

        if (wrap):
            return build_http_response(serializer_response.data, status.HTTP_200_OK)
        else:
            return Response(serializer_response.data, status=status.HTTP_200_OK)
    else:
        return build_http_response('view_list() Your license has expired. Please ask the account administrator to renew the subscription.',
                        status.HTTP_401_UNAUTHORIZED)


def get_file_extension(file_name, decoded_file):
    import imghdr

    extension = imghdr.what(file_name, decoded_file)
    extension = "jpg" if extension == "jpeg" else extension

    return extension


def close_sighting(sighting, new_sighting_detector=None):
    sighting.is_active = False
    sighting.save()
    logger.debug('close_sighting() Sighting \'%s\' is no longer current.', sighting)

    check_for_events_async(sighting, new_sighting_detector)


def trigger_event_actions(event, sighting):
    logger.info('trigger_event_actions() Conditions met for event \'%s\'. Creating EventOccurrence and triggering actions...', event)
    event_occurrence = EventOccurrence.objects.create(event=event, sighting=sighting)

    # check for limits associated with this sighting in a different thread
    # t = threading.Thread(target=check_for_limits, args=(event_occurrence,))
    # t.start()

    metadata = json.loads(event.metadata)
    if metadata['actions']:
        for action in metadata['actions']:
            actions.perform_action(action, event, sighting.beacon, sighting.detector, None)


def trigger_limit_actions(limit, event, beacon):
    logger.info('trigger_limit_actions() Conditions met for limit \'%s\'. Triggering corresponding actions...', limit)
    limit_occurrence = LimitOccurrence.objects.create(limit=limit, event=event, beacon=beacon)

    metadata = json.loads(limit.metadata)
    if metadata['actions']:
        for action in metadata['actions']:
            actions.perform_action(action, event, beacon, None, limit)


def scheduled_check_for_event(event, sighting, seconds_in_the_future, iteration=1):
    logger.debug('scheduled_check_for_event() Going to sleep for %ds...', seconds_in_the_future)
    time.sleep(seconds_in_the_future if seconds_in_the_future > 0 else 1)
    logger.debug('scheduled_check_for_event() Checking if \'%s\' event conditions are met...', event)

    new_sightings = Sighting.objects.filter(beacon=sighting.beacon, first_seen_at__gt=sighting.last_seen_at)
    if event.detectors is not None and len(event.detectors.all()) > 0:
        new_sightings = new_sightings.filter(detector__in=event.detectors.all())

    new_sightings = new_sightings.order_by('-id')[:1]
    logger.warn(str(new_sightings.query))
    if new_sightings is None or len(new_sightings) == 0:
        trigger_event_actions(event, sighting)

        # if dormant_period > 0, schedule new check for when that period ends
        event_metadata = json.loads(event.metadata)
        event_sighting_dormant_period_in_seconds = event_metadata.get('sighting_dormant_period_in_seconds', 0)
        if event_sighting_dormant_period_in_seconds > 0:
            # TODO: as a precaution not to keep a never dying thread, only iterate X times.
            # Need to refactor this in any case: instead of sleeping a thread, have a schedules table and a cron job
            # that runs every "minute" and checks for "tasks". Sleeping threads are bad....
            if iteration < 3:
                t = threading.Thread(target=scheduled_check_for_event, args=(event, sighting, event_sighting_dormant_period_in_seconds, iteration+1))
                t.start()
            else:
                logger.warn('scheduled_check_for_event() Already ran 3 times so that\'s enough. No more checks for this sighting.')
    else:
        logger.info('scheduled_check_for_event() Conditions not met for event \'%s\'. ' +
                    'The corresponding beacon has been active in the meantime...', event)


def check_for_events_async(sighting, new_sighting_detector=None):
    # check for events associated with this sighting in a different  thread
    t = threading.Thread(target=check_for_events, args=(sighting, new_sighting_detector))
    t.start()


def check_for_events(sighting, new_sighting_detector=None):
    logger.debug('check_for_events() Checking for events associated with sighting \'%s\'...', sighting)
    now = datetime.now(timezone.utc)
    current_week_day_representation = math.pow(2, now.weekday())

    raw_query = Event.objects.raw('SELECT e.* ' +
                                  'FROM ivigilate_event e ' +
                                  'LEFT OUTER JOIN ivigilate_event_unauthorized_beacons eb ON e.id = eb.event_id ' +
                                  'LEFT OUTER JOIN ivigilate_event_detectors ed ON e.id = ed.event_id ' +
                                  'WHERE (e.is_active = True ' +
                                  'AND e.account_id = %s ' +
                                  'AND (eb.beacon_id IS NULL OR eb.beacon_id = %s) ' +
                                  'AND (ed.detector_id IS NULL OR ed.detector_id = %s) ' +
                                  'AND e.schedule_days_of_week & %s > 0 ' +
                                  'AND e.schedule_start_time <= (%s + interval \'1m\' * e.schedule_timezone_offset) :: time ' +
                                  'AND e.schedule_end_time >= (%s + interval \'1m\' * e.schedule_timezone_offset) :: time)',
                                  [sighting.detector.account_id, sighting.beacon.id,
                                   sighting.detector.id if sighting.detector is not None else 0,
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
        logger.debug('check_for_events() Found %s event(s) active for sighting \'%s\'.', len(events), sighting)
        for event in events:
            logger.debug('check_for_events() Checking if \'%s\' event conditions are met...', event)
            conditions_met = False
            event_metadata = json.loads(event.metadata)
            sighting_metadata = json.loads(sighting.metadata or '{}')
            initial_timestamp = sighting_metadata.get('timestamp_event_id_' + str(event.id), None)

            # Check if the bulk of the conditions are met...
            if event_metadata.get('event_is_local', False) == False and \
                            event_metadata.get('sighting_is_active', True) == sighting.is_active and \
                            event_metadata.get('sighting_has_battery_below', 0) >= sighting.beacon_battery and \
                    (event_metadata.get('sighting_has_comment', None) is None or
                         (event_metadata['sighting_has_comment'] and sighting.comment) or
                         (not event_metadata['sighting_has_comment'] and not sighting.comment)) and \
                    (event_metadata.get('sighting_has_been_confirmed', None) is None or
                         (event_metadata['sighting_has_been_confirmed'] and sighting.confirmed) or
                         (not event_metadata['sighting_has_been_confirmed'] and not sighting.confirmed)) and \
                    (event_metadata.get('sighting_max_rssi', 0) >= sighting.rssi and
                         (event_metadata.get('sighting_min_rssi', -99) < sighting.rssi)):
                    # and \
                    # (new_sighting_detector is None or len(event.detectors.all()) == 0 or new_sighting_detector in event.detectors.all()):

                # TODO: use the new_sighting_detector to keep an event alive when moving between detectors ^^^^
                # Check the sighting duration within the proximity range specified in the event
                event_sighting_duration_in_seconds = event_metadata.get('sighting_duration_in_seconds', 0)
                if event_sighting_duration_in_seconds > 0:
                    if not sighting.is_active:
                        seconds_in_the_future = event_sighting_duration_in_seconds - (now - sighting.last_seen_at).total_seconds()
                        # schedule check for missing beacon (to occur after X seconds)
                        t = threading.Thread(target=scheduled_check_for_event, args=(event, sighting, seconds_in_the_future))
                        t.start()
                    else:
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
                    # Check if we should trigger the same actions over and over again (or only once per sighting)
                    once_per_sighting = event_metadata.get('once_per_sighting', False)
                    same_occurrence_count = EventOccurrence.objects.filter(event=event, sighting=sighting).count()
                    if not once_per_sighting or same_occurrence_count == 0:
                        previous_occurrences = EventOccurrence.objects.filter(event=event,
                                                                              sighting__beacon=sighting.beacon,
                                                                              sighting__detector=sighting.detector
                                                                             ).order_by('-id')[:1]
                        event_sighting_dormant_period_in_seconds = event_metadata.get('sighting_dormant_period_in_seconds', 0)
                        if (event_sighting_dormant_period_in_seconds <= 0 or
                                previous_occurrences is None or len(previous_occurrences) == 0 or
                                now - timedelta(seconds=event_sighting_dormant_period_in_seconds) > previous_occurrences[0].occurred_at):
                            trigger_event_actions(event, sighting)

                            sighting_metadata['timestamp_event_id_' + str(event.id)] = None
                            sighting.metadata = json.dumps(sighting_metadata)
                            sighting.save()
                        else:
                            logger.debug('check_for_events() Conditions met for event \'%s\' but skipping it has ' + \
                                         'the tuple event / beacon / detector is still in the dormant period.', event)
                    else:
                        logger.debug('check_for_events() Conditions met for event \'%s\' ' + \
                                     'but the required actions were already triggered once for this sighting.', event)
                else:  # event conditions require that a specific previous event had occurred
                    previous_occurrences = EventOccurrence.objects.filter(sighting__beacon=sighting.beacon).order_by('-id')[:2]
                    if (previous_occurrences is not None and len(previous_occurrences) > 0 and
                                previous_occurrences[0].event_id == event_metadata['sighting_previous_event']['id']):
                        if (len(previous_occurrences) > 1 and (previous_occurrences[0].sighting_id != sighting.id or
                                    previous_occurrences[1].event_id != event.id)):
                            trigger_event_actions(event, sighting)
                        else:
                            logger.debug('check_for_events() Conditions met for event \'%s\' ' +
                                     'but the required actions were already triggered once for this sighting.', event)
                    else:
                        logger.info('check_for_events() Conditions not met for event \'%s\'. ' +
                                    'Previous event occurrence doesn\'t match configured one', event)
            else:
                logger.info('check_for_events() Conditions not met for event \'%s\'. ', event)


def check_for_limits(event_occurrence):
    logger.debug('check_for_limits() Checking for limits associated with event_occurrence \'%s\'...', event_occurrence)

    limits = Limit.objects.filter(Q(is_active=True),
                                        Q(events=None)|Q(events__id__exact=event_occurrence.event.id),
                                        Q(beacons=None)|Q(beacons__id__exact=event_occurrence.sighting.beacon.id),
                                        Q(start_date__lte=event_occurrence.occurred_at)
                                        ).order_by('-start_date')[:1]

    if limits:
        logger.debug('check_for_limits() Found %s limit(s) active for event_occurrence \'%s\'.', len(limits), event_occurrence)
        for limit in limits:
            logger.debug('check_for_limits() Checking if \'%s\' limit conditions are met...', limit)
            metadata = json.loads(limit.metadata)
            filter_date_limit = datetime.strptime(metadata['occurrence_date_limit'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.UTC) + \
                                timedelta(days=1) if metadata.get('occurrence_date_limit', None) is not None else None
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

                if metadata['consider_each_beacon_separately']:
                    eos = eos.filter(sighting__beacon=event_occurrence.sighting.beacon)
                elif (limit.beacons and limit.beacons.count() > 0):
                    eos = eos.filter(sighting__beacon__in=limit.beacons.all())

                if (eos.count() > metadata['occurrence_count_limit']):
                    logger.debug('check_for_limits() Conditions met for limit \'%s\' with event occurrence \'%s\' due to going over the count limit.',
                                 len(limits), event_occurrence)
                    trigger_limit_actions(limit, event_occurrence.event, event_occurrence.sighting.beacon)
                else:
                    logger.info('check_for_limits() Conditions not met for limit \'%s\'. ', limit)
            else:
                logger.info('check_for_limits() Conditions not met for limit \'%s\'. ', limit)
