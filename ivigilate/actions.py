from datetime import datetime, timezone, timedelta
from ivigilate import settings
from twilio.rest import TwilioRestClient
from ivigilate.models import Notification
from django.core.mail import send_mail
import json, re, logging, requests, threading

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def replace_tags(msg, event=None, beacon=None, detector=None, limit=None, sighting=None):
    now = datetime.now(timezone.utc)
    return msg.replace('%company_id%', event.account.company_id if event is not None else ''). \
        replace('%event_id%', event.reference_id if event is not None else ''). \
        replace('%event_name%', event.name if event is not None else ''). \
        replace('%beacon_id%', (beacon.reference_id or beacon.uid) if beacon is not None else ''). \
        replace('%beacon_name%', beacon.name if beacon is not None else ''). \
        replace('%detector_id%', (detector.reference_id or detector.uid) if detector is not None else ''). \
        replace('%detector_name%', detector.name if detector is not None else ''). \
        replace('%limit_id%', limit.reference_id if limit is not None else ''). \
        replace('%limit_name%', limit.name if limit is not None else ''). \
        replace('%occur_date%', now.strftime('%Y-%m-%dT%H:%M:%S')). \
        replace('%sighting_metadata%', sighting.metadata.replace('"','\"') if sighting is not None else '{}')


def create_notification(event, metadata):
    previous_notifications = Notification.objects.filter(event=event, is_active=True). \
                                            order_by('-id')[:1]

    if previous_notifications is None or len(previous_notifications) == 0:
        Notification.objects.create(account=event.account, event=event, metadata=metadata)


def send_twilio_message(recipients, msg):
    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    for to in re.split(',|;', recipients):
        message = client.messages.create(
            body=msg,
            to=to,
            from_=settings.TWILIO_DEFAULT_CALLERID
        )


def send_email(subject, body, recipients):
    send_mail(subject,
              body,
              settings.DEFAULT_FROM_EMAIL,
              re.split(',|;', recipients),
              fail_silently=False)


def make_rest_call(method, uri, body):
    if method == 'GET':
        requests.get(uri, body)
    elif method == 'POST':
        requests.post(uri, body)
    elif method == 'PUT':
        requests.put(uri, body)


def perform_action_async(action, event, beacon, detector, limit, sighting):
    t = threading.Thread(target=perform_action, args=(action, event, beacon, detector, limit, sighting,))
    t.start()


def perform_action(action, event, beacon, detector, limit, sighting):
    try:
        if action['type'] == 'NOTIFICATION':
            logger.info('perform_action() Action for ' + ('event' if event is not None else 'limit') + ' \'%s\': Generating On-Screen Notification.',
                        event if event is not None else limit)
            action_metadata = {}
            action_metadata['category'] = action['category']
            action_metadata['timeout'] = action.get('timeout', 0)
            action_metadata['title'] = replace_tags(action.get('title', ''), event, beacon, detector, limit, sighting)
            action_metadata['message'] = replace_tags(action.get('message', ''), event, beacon, detector, limit, sighting)

            create_notification(event, json.dumps(action_metadata))
        elif action['type'] == 'SMS':
            logger.info('perform_action() Action for ' + ('event' if event is not None else 'limit') + ' \'%s\': Sending SMS to %s recipient(s).',
                    event if event is not None else limit, len(re.split(',|;', action['recipients'])))
            message = replace_tags(action.get('message', ''), event, beacon, detector, limit, sighting)

            send_twilio_message(action['recipients'], message)
        elif action['type'] == 'EMAIL':
            logger.info('perform_action() Action for ' + ('event' if event is not None else 'limit') + ' \'%s\': Sending EMAIL to %s recipient(s).',
                    event if event is not None else limit, len(re.split(',|;', action['recipients'])))
            body = replace_tags(action.get('body', ''), event, beacon, detector, limit, sighting)
            subject = replace_tags(action.get('subject', ''), event, beacon, detector, limit, sighting)

            send_email(subject, body, action['recipients'])
        elif action['type'] == 'REST':
            uri = replace_tags(action['uri'], event, beacon, detector, limit, sighting)
            body = replace_tags(action.get('body', ''), event, beacon, detector, limit, sighting)
            body = json.loads(body)
            logger.info('perform_action() Action for ' + ('event' if event is not None else 'limit') + ' \'%s\': Making a \'%s\' call to \'%s\' with the following payload: %s',
                    event if event is not None else limit, action['method'], uri, body)

            make_rest_call(action['method'], uri, body)
    except Exception as ex:
        logger.exception('perform_action() Failed to perform action of type \'%s\':', action['type'])
