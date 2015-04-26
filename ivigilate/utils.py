from datetime import datetime, timezone, timedelta
from twilio.rest import TwilioRestClient
from ivigilate import settings
from ivigilate.models import Sighting, Event, EventOccurrence
import math, json, re, logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def get_file_extension(file_name, decoded_file):
    import imghdr

    extension = imghdr.what(file_name, decoded_file)
    extension = "jpg" if extension == "jpeg" else extension

    return extension


def send_twilio_message(to, msg):
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body = msg,
        to = to,
        from_ = settings.TWILIO_DEFAULT_CALLERID,
    )


def close_sighting(sighting, newPlace=None, newUser=None):
    sighting.is_current = False
    check_for_events(sighting, newPlace, newUser)
    sighting.save()
    logger.debug('Sighting \'%s\' is no longer current.', sighting)


def check_for_events(sighting, newPlace=None, newUser=None):
    logger.debug('Checking for events associated with sighting \'%s...\'', sighting)
    now = datetime.now(timezone.utc)
    current_week_day_representation = math.pow(2, now.weekday())
    events = Event.objects.filter(is_active=True,
                                  movables__id__exact=sighting.movable.id,
                                  places__id__exact=sighting.place.id,
                                  schedule_days_of_week__bwand=current_week_day_representation,
                                  schedule_start_time__lte=now,
                                  schedule_end_time__gte=now)
    if events:
        logger.debug('Found %s event(s) active for sighting \'%s\'.', len(events), sighting)
        for event in events:
            logger.debug('Checking if \'%s\' event conditions are met.', event)
            if event.sighting_is_current == sighting.is_current and \
                event.sighting_has_battery_below >= (sighting.battery or 0) and \
                ((event.sighting_has_comment is None) or
                 (event.sighting_has_comment and sighting.comment) or
                 (not event.sighting_has_comment and not sighting.comment)) and \
                ((event.sighting_has_been_confirmed is None) or
                 (event.sighting_has_been_confirmed and sighting.confirmed) or
                 (not event.sighting_has_been_confirmed and not sighting.confirmed)) and \
                (not newPlace or newPlace in event.places) and \
                (not newUser or newUser in event.places):
                logger.debug('Conditions met for event \'%s\'. ' + \
                             'Creating EventOccurrence and triggering actions...', event)
                EventOccurrence.objects.create(event=event, sighting=sighting, movable=sighting.movable)

                metadata = json.loads(event.metadata)
                actions = metadata['actions']
                if actions:
                    for action in actions:
                        if action['type'] == 'SMS':
                            logger.debug('Action for event \'%s\': Sending SMS to %s recipient(s).',
                                         event, len(re.split(',|;', action['recipients'])))
                            for to in re.split(',|;', action['recipients']):
                                send_twilio_message(to, event.name)




