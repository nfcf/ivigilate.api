from datetime import datetime, timezone, timedelta
from twilio.rest import TwilioRestClient
from django.core.mail import send_mail
from ivigilate import settings
from ivigilate.models import Sighting, Event, EventOccurrence
from django.db.models import Q
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
    events = Event.objects.filter(Q(is_active=True),
                                  Q(movables=None)|Q(movables__id__exact=sighting.movable.id),
                                  Q(places=None)|Q(places__id__exact=sighting.place.id),
                                  Q(schedule_days_of_week__bwand=current_week_day_representation),
                                  Q(schedule_start_time__lte=now),
                                  Q(schedule_end_time__gte=now))
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

                # Make sure we don't trigger the same actions over and over again (only once per sighting)
                previous_occurrences = EventOccurrence.objects.filter(event=event, sighting=sighting).order_by('id')[:1]
                if (previous_occurrences is None or len(previous_occurrences) == 0):
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
                                    send_twilio_message(to, action['message'])
                            elif action['type'] == 'EMAIL':
                                logger.debug('Action for event \'%s\': Sending EMAIL to %s recipient(s).',
                                             event, len(re.split(',|;', action['recipients'])))
                                send_mail(action['subject'], action['body'], settings.DEFAULT_FROM_EMAIL,
                                          re.split(',|;', action['recipients']), fail_silently=False)



