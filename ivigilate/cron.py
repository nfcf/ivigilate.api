from django_cron import CronJobBase, Schedule
from ivigilate.models import Sighting, Account, License
from datetime import datetime, timezone, timedelta
from ivigilate.utils import close_sighting
from time import sleep
import logging, json

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class RecurringLicensesJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # 1 day
    RETRY_AFTER_FAILURE_MINS = 720  # 1/2 day

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'ivigilate.recurring_licenses_job'  # a unique code

    def do(self):
        logger.debug('Starting RecurringLicensesJob...')
        accounts = Account.objects.filter()
        if accounts:
            for account in accounts:
                if account.get_license_about_to_expire() is not None and account.get_license_due_for_payment() is None:
                    logger.debug('Found account that needs to renew the license in a few days: \'%s\'', account)
                    try:
                        account_metadata = json.loads(account.metadata)
                        if 'plan' in account_metadata:
                            license_metadata = {}  # dict()
                            license_metadata['duration_in_months'] = account_metadata['plan']['duration_in_months']
                            license_metadata['max_users'] = account_metadata['plan']['max_users']
                            license_metadata['max_beacons'] = account_metadata['plan']['max_beacons']
                            license = License.objects.create(account=account,
                                                             amount=account_metadata['plan']['amount'],
                                                             currency=account_metadata['plan']['currency'],
                                                             description='%s Month(s) Subscription' % str(account_metadata['plan']['duration_in_months']),
                                                             metadata=json.dumps(license_metadata))
                            logger.debug('Generated a new License item for account: \'%s\'.', account)
                        else:
                            logger.warning('No subscription plan metadata information available for account: \'%s\'.', account)
                    except Exception as ex:
                        logger.exception('Failed to generate License for account: \'%s\'', account)
        logger.debug('Finished RecurringLicensesJob...')


class CloseSightingsJob(CronJobBase):
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'ivigilate.close_sightings_job'  # a unique code

    def do(self):
        NUMBER_OF_SECONDS_TO_BE_CONSIDERED_OLD = 10
        NUMBER_OF_TIMES_TO_RUN = 3  # since cron only runs every minute...trying to minimize the interval
        iteration = 1
        try:
            while iteration <= NUMBER_OF_TIMES_TO_RUN:
                logger.debug('Starting CloseSightingsJob iteration %s...', iteration)
                now = datetime.now(timezone.utc)
                filter_datetime = now - timedelta(seconds=NUMBER_OF_SECONDS_TO_BE_CONSIDERED_OLD)
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

