from django_cron import CronJobBase, Schedule
from django_cron.models import CronJobLog

from ivigilate.models import Sighting, Account, License
from datetime import datetime, timezone, timedelta
from ivigilate.utils import close_sighting
from time import sleep
import logging, json, threading

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ClearCronLogsJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # 1 day
    RETRY_AFTER_FAILURE_MINS = 720  # 1/2 day

    NUMBER_OF_DAYS_TO_BE_CONSIDERED_OLD = 7

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'ivigilate.clear_cron_logs_job'  # a unique code

    def do(self):
        logger.debug('ClearCronLogsJob.do() Starting...')
        now = datetime.now(timezone.utc)
        filter_datetime = now - timedelta(days=ClearCronLogsJob.NUMBER_OF_DAYS_TO_BE_CONSIDERED_OLD)
        CronJobLog.filter(end_time__lt=filter_datetime).delete()
        logger.debug('RecurringLicensesJob.do() Finished...')


class RecurringLicensesJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # 1 day
    RETRY_AFTER_FAILURE_MINS = 720  # 1/2 day

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'ivigilate.recurring_licenses_job'  # a unique code

    def do(self):
        logger.debug('RecurringLicensesJob.do() Starting...')
        accounts = Account.objects.filter()
        if accounts:
            for account in accounts:
                if account.get_license_about_to_expire() is not None and account.get_license_due_for_payment() is None:
                    logger.debug('RecurringLicensesJob.do() Found account that needs to renew the license in a few days: \'%s\'', account)
                    try:
                        account_metadata = json.loads(account.metadata)
                        if 'plan' in account_metadata:
                            license_metadata = {}  # dict()
                            license_metadata['duration_in_months'] = account_metadata['plan']['duration_in_months']
                            license_metadata['max_detectors'] = account_metadata['plan']['max_detectors']
                            license_metadata['max_beacons'] = account_metadata['plan']['max_beacons']
                            license = License.objects.create(account=account,
                                                             amount=account_metadata['plan']['amount'],
                                                             currency=account_metadata['plan']['currency'],
                                                             description='%s Month(s) Subscription' % str(account_metadata['plan']['duration_in_months']),
                                                             metadata=json.dumps(license_metadata))
                            logger.debug('RecurringLicensesJob.do() Generated a new License item for account: \'%s\'.', account)
                        else:
                            logger.warning('RecurringLicensesJob.do() No subscription plan metadata information available for account: \'%s\'.', account)
                    except Exception as ex:
                        logger.exception('RecurringLicensesJob.do() Failed to generate License for account: \'%s\'', account)
        logger.debug('RecurringLicensesJob.do() Finished...')


class CloseSightingsJob(CronJobBase):
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1

    NUMBER_OF_SECONDS_TO_BE_CONSIDERED_OLD = 6
    NUMBER_OF_TIMES_TO_RUN = 6  # since cron only runs every minute...trying to minimize the interval

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'ivigilate.close_sightings_job'  # a unique code

    def do(self):
        iteration = 1
        try:
            while iteration <= CloseSightingsJob.NUMBER_OF_TIMES_TO_RUN:
                t = threading.Thread(target=self.asyncJob, args=(iteration,))
                t.start()
                iteration +=1
                sleep(10)
        except Exception as ex:
            logger.exception('CloseSightingsJob.do() failed with exception:')

    def asyncJob(self, iteration):
        logger.debug('CloseSightingsJob.do() Starting iteration %s...', iteration)
        now = datetime.now(timezone.utc)
        filter_datetime = now - timedelta(seconds=CloseSightingsJob.NUMBER_OF_SECONDS_TO_BE_CONSIDERED_OLD)
        sightings = Sighting.objects.filter(type='A', is_active=True, last_seen_at__lt=filter_datetime)
        if sightings:
            logger.info('CloseSightingsJob.do() Found %s sighting(s) that need closing.', len(sightings))
            for sighting in sightings:
                close_sighting(sighting)
        logger.debug('CloseSightingsJob.do() Finished iteration %s...', iteration)