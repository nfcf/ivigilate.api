from django_cron import CronJobBase, Schedule
from twilio.rest import TwilioRestClient
from ivigilate.models import Sighting, Event, EventOccurrence
from datetime import datetime, timezone, timedelta
from django.conf import settings
import json
import re
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class RulesEngineJob(CronJobBase):
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'ivigilate.rules_engine_job'    # a unique code

    def close_sightings(self):
        sightings = Sighting.objects.filter(is_current=True)
        if sightings:
            now = datetime.now(timezone.utc)
            for sighting in sightings:
                if (now - sighting.last_seen_at).seconds > 30:
                    sighting.is_current = False
                    sighting.save()

    def send_twilio_message(self, to, msg):
        client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body = msg, #"Hello again! Yet another test...",  # Message body, if any
            to = to, #"+353831457316", #,+351967560446",
            from_ = settings.TWILIO_DEFAULT_CALLERID,
        )


    def event_checking(self):
        try:
            print('executing...')
            now = datetime.now(timezone.utc)
            events = Event.objects.filter(is_active=True)
            if events:
                for event in events:
                    filter_date = now - timedelta(seconds=event.sighting_duration_in_seconds + 60)
                    metadata = json.loads(event.metadata)
                    #trigger_is_current = metadata['trigger']['is_current'] in ['true', 'True','1']
                    #trigger_duration = int(metadata['trigger']['duration'])
                    actions = metadata['actions']

                    if event.movables:
                        for movable in event.movables.all():
                            sightings = Sighting.objects.filter(last_seen_at__gte=filter_date, movable=movable).order_by('-last_seen_at')
                            if sightings and event.places:
                                sightings = sightings.filter(watcher_uid__in=event.places.values('uid'))
                            if sightings:
                                total_duration = 0
                                for sighting in sightings.all():
                                    total_duration += sighting.get_duration()

                                print('pre check')
                                if sightings[0].is_current == event.sighting_is_current and \
                                                total_duration > event.sighting_duration_in_seconds and \
                                                sightings[0].battery <= event.sighting_has_battery_below:
                                    #create an EventOccurrence here, regarding of having actions or not
                                    occurrence = EventOccurrence.objects.create(event=event,movable=movable,duration_in_seconds=total_duration)
                                    occurrence.sightings.add(*sightings)
                                    if actions:
                                        for action in actions:
                                            if action['type'] == 'SMS':
                                                for to in re.split(',|;', action['recipients']):
                                                    self.send_twilio_message(to, event.name)

                    else:
                        if event.places:
                            sightings = Sighting.objects.filter(watcher_uid__in=event.places.values('uid'))
                        if sightings:
                            a = sightings[0]  #################
        except Exception as ex:
            print(str(ex))



    def do(self):
        self.close_sightings()
        self.event_checking()

