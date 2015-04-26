from django_cron import CronJobBase, Schedule
from ivigilate.models import Sighting
from datetime import datetime, timezone, timedelta
from ivigilate.utils import close_sighting
from time import sleep
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CloseSightingsJob(CronJobBase):
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'ivigilate.close_sightings_job'  # a unique code

    def do(self):
        FILTER_OLD_NUMBER_OF_SECONDS = 10
        NUMBER_OF_TIMES_TO_RUN = 3  # since cron only runs every minute...trying to minimize the interval
        iteration = 1
        try:
            while iteration <= NUMBER_OF_TIMES_TO_RUN:
                logger.debug('Starting CloseSightingsJob iteration %s...', iteration)
                now = datetime.now(timezone.utc)
                filter_datetime = now - timedelta(seconds=FILTER_OLD_NUMBER_OF_SECONDS)
                sightings = Sighting.objects.filter(is_current=True, last_seen_at__lt=filter_datetime)
                if sightings:
                    logger.debug('Found %s sighting(s) that need closing.', len(sightings))
                    for sighting in sightings:
                        close_sighting(sighting)
                logger.debug('Finished CloseSightingsJob iteration %s...', iteration)
                iteration +=1
                sleep(10)
        except Exception as ex:
            logger.exception('CloseSightingsJob failed with exception:')

