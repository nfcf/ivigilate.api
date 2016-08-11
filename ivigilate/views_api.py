import json
import logging
import threading
import time
from datetime import datetime

import os
import stripe
from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.forms import model_to_dict
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView
from rest_framework import permissions, status, views
from rest_framework.response import Response

from ivigilate import utils
from ivigilate.serializers import *

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class IndexView(TemplateView):
    template_name = 'index.html'

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)


class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = json.loads(request.body.decode('utf-8'))

        email = data.get('email', None)
        password = data.get('password', None)
        metadata = data.get('metadata', None)

        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)

                Token.objects.get_or_create(user=user) # creates token if necessary...will fetch it in the AuthUser model (get_token())

                if metadata is not None and len(metadata.strip()) > 0:
                    now = datetime.now(timezone.utc)
                    metadata = json.loads(metadata)
                    metadata['device']['last_login_date'] = now.strftime('%Y-%m-%d %H:%M')
                    if user.metadata is not None and len(user.metadata.strip()) > 0:
                        user_metadata = json.loads(user.metadata)
                        existing_device = next(
                            (device for device in user_metadata['devices'] if device.get('uid', '') == metadata['device'].get('uid', '')), None)
                        if existing_device is not None:
                            existing_device['last_login_date'] = now.strftime('%Y-%m-%d %H:%M')
                    else:
                        user_metadata = {}
                        user_metadata['devices'] = []
                        user_metadata['devices'].append(metadata['device'])

                    user.metadata = json.dumps(user_metadata)
                    user.save()

                serialized = AuthUserReadSerializer(user, context={'request': request})

                return utils.build_http_response(serialized.data, status.HTTP_200_OK)
            else:
                return utils.build_http_response('This user has been disabled.', status.HTTP_401_UNAUTHORIZED)
        else:
            return utils.build_http_response('Invalid email/password combination.', status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)

        return utils.build_http_response({}, status.HTTP_200_OK)


class ProvisionDeviceView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None

        if account:
            data = json.loads(request.body.decode('utf-8'))

            type = data.get('type', None)
            uid = data.get('uid', None)
            name = data.get('name', None)
            metadata = data.get('metadata', '')
            is_active = data.get('is_active', True)
            # serialized = None

            if uid is None or len(uid) == 0:
                return utils.build_http_response('UID field cannot be empty.',
                                                 status.HTTP_400_BAD_REQUEST)

            uid = uid.lower()
            if type[0] == 'B':
                try:
                    beacon = Beacon.objects.get(account=account, uid=uid)
                    beacon.type = type[1]
                    beacon.name = name
                    beacon.metadata = metadata
                    beacon.is_active = is_active
                    beacon.save()
                    return utils.build_http_response('Beacon already provisioned for this account. Info updated.',
                                             status.HTTP_200_OK)
                except Beacon.DoesNotExist:
                    beacon = Beacon.objects.create(account=account, uid=uid, name=name, type=type[1], metadata=metadata)


            elif type[0] == 'D':
                try:
                    detector = Detector.objects.get(account=account, uid=uid)
                    detector.type = type[1] if type[1] == 'F' else 'M'  # Remove this if else check in a later release (protection for having removed the 'User' detector type
                    detector.name = name
                    detector.metadata = metadata
                    detector.is_active = is_active
                    detector.save()
                    return utils.build_http_response('Detector already provisioned for this account. Info updated.',
                                             status.HTTP_200_OK)
                except Detector.DoesNotExist:
                    detector = Detector.objects.create(account=account, uid=uid, name=name, type=type[1], metadata=metadata)



            return utils.build_http_response('Success!', status.HTTP_200_OK)
        else:
            return utils.build_http_response('The current logged on user is not associated with any account.',
                                     status.HTTP_400_BAD_REQUEST)


class AddSightingsView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = json.loads(request.body.decode('utf-8'))
        now_timestamp = time.time() * 1000

        ignored_beacons = []
        invalid_beacons = []

        if (data is not None and len(data) > 0):
            logger.info('AddSightingsView.post() Got %s sightings', len(data))
            for sighting in data:

                timestamp = sighting.get('timestamp', None)
                type = sighting.get('type', 'AC')

                detector_uid = sighting.get('detector_uid').lower()
                detector_battery = sighting.get('detector_battery', None)
                beacon_mac = sighting.get('beacon_mac', None)
                if beacon_mac is not None:
                    beacon_mac = beacon_mac.lower()
                beacon_uid = sighting.get('beacon_uid', None)
                if beacon_uid is not None:
                    beacon_uid = beacon_uid.lower()
                beacon_battery = sighting.get('beacon_battery', None)

                rssi = sighting.get('rssi', None)
                location = sighting.get('location', None)
                metadata = sighting.get('metadata', '{}')

                is_active = sighting.get('is_active', True)  # for now, only mobile apps are smart enough to send this set to False...

                logger.info('AddSightingsView.post() Sighting: %s %s %s %s %s %s %s %s %s %s %s %s',
                            timestamp, type, detector_uid, detector_battery, beacon_mac, beacon_uid, beacon_battery,
                            rssi, is_active, metadata, location, is_active)



                # if now_timestamp - timestamp > utils.TIMESTAMP_DIFF_ALLOWED:
                #    logger.error('AddSightingsView.post() ignoring sighting with outdated timestamp...')
                #    return utils.build_http_response('Ignoring sighting with outdated timestamp.',
                #                                     status.HTTP_400_BAD_REQUEST)

                detectors = Detector.objects.filter(is_active=True, uid=detector_uid)  # this can yield more than one detector...
                if len(detectors) > 0:
                    if type != 'GPS':
                        beacons = Beacon.objects.filter(Q(is_active=True),
                                                        Q(uid=beacon_mac) | Q(uid=beacon_uid))  # this can yield more than one beacon...
                    for detector in detectors:
                        if location is not None:
                            location_parsed = json.dumps(location)
                        else:
                            location_parsed = detector.location

                        if detector.account.get_license_in_force() is None:
                            logger.warning('AddSightingsView.post() Ignoring sighting as the associated Account doesn\'t have a valid subscription.')
                            # TODO: Need to move this somewhere else as there can be more than one detector
                            # return utils.build_http_response('Ignoring sighting as the associated Account doesn\'t have a valid subscription.',
                            #                                  status.HTTP_402_PAYMENT_REQUIRED)

                        if (type == 'GPS'):
                            self.open_sighting_async(detector, detector_battery, None, 0, rssi,
                                                     location_parsed, metadata, type, None)
                        elif len(beacons) > 0:
                            for beacon in beacons:
                                if beacon.type == 'F' and beacon.location is not None:
                                    location_parsed = beacon.location

                                if beacon.type == 'M':
                                    previous_sightings = Sighting.objects.filter(is_active=True, beacon=beacon, detector__account=detector.account). \
                                                            order_by('-last_seen_at')[:1]
                                else:
                                    previous_sightings = Sighting.objects.filter(is_active=True, detector=detector, detector__account=detector.account). \
                                                            order_by('-last_seen_at')[:1]

                                if len(previous_sightings) > 0:
                                    previous_sighting = previous_sightings[0]

                                if is_active:
                                    # Only open the sighting if 'AutoClosing' or if RSSI is greater than the configured value for the detector or rssi within 5% range of previous_sighting.rssi
                                    previous_sighting_rssi = previous_sighting.rssi if previous_sighting.rssi is not None else 0
                                    if type == 'AC' or \
                                            (previous_sighting is None and rssi >= detector.arrival_rssi) or \
                                            (beacon.type == 'M' and (previous_sighting.detector == detector or rssi * 1.05 > previous_sighting_rssi)) or \
                                            (detector.type == 'M' and (previous_sighting.beacon == beacon or rssi * 1.05 > previous_sighting_rssi)):
                                        self.open_sighting_async(detector, detector_battery, beacon, beacon_battery, rssi, location_parsed, metadata, type, previous_sighting)
                                    else:
                                        logger.info('AddSightingsView.post() Ignored Beacon MAC / UID as the rssi is lower than the ' +
                                            'arrival_rssi configured for this detector / user (%s < %s)', rssi,
                                            detector.arrival_rssi)
                                        ignored_beacons.append(beacon_mac + beacon_uid)
                                else:
                                    self.close_sighting_async(detector, detector_battery, beacon, beacon_battery, rssi, location_parsed, metadata)
                        else:
                            logger.warning('AddSightingsView.post() Invalid Beacon MAC / UID (couldn\'t find corresponding active device).')
                            invalid_beacons.append(beacon_mac + beacon_uid)

                else:
                    logger.warning('AddSightingsView.post() Invalid Detector UID (couldn\'t find corresponding active device).')
                    return utils.build_http_response('Invalid Detector UID (couldn\'t find corresponding active device).',
                        status.HTTP_401_UNAUTHORIZED)

        # serialized = SightingReadSerializer(new_sighting, context={'request': request})
        # return Response(serialized.data)
        if len(ignored_beacons) > 0 or len(invalid_beacons) > 0:
            response = {}
            response["ignored_beacons"] = ignored_beacons
            response["invalid_beacons"] = invalid_beacons
            return utils.build_http_response(response, status.HTTP_206_PARTIAL_CONTENT)
        else:
            return utils.build_http_response(None, status.HTTP_200_OK)

    def open_sighting_async(self, detector, detector_battery, beacon, beacon_battery, rssi, location, metadata, type, previous_sighting):
        # check for events associated with this sighting in a different  thread
        t = threading.Thread(target=self.open_sighting,
                             args=(detector, detector_battery, beacon, beacon_battery, rssi, location, metadata, type, previous_sighting))
        t.start()

    def open_sighting(self, detector, detector_battery, beacon, beacon_battery, rssi, location, metadata, type, previous_sighting):
        REPORTED_MISSING_NOTIFICATION_EVERY_MINS = 1
        logger.debug('open_sighting() Started...')

        now = datetime.now(timezone.utc)

        previous_sighting_occurred_at = None
        new_sighting = None
        if previous_sighting is not None:
            previous_sighting_rssi = previous_sighting.rssi if previous_sighting.rssi is not None else 0

            # if the abs_diff between the 2 rssi values is bigger than X, "ignore" most recent value
            step_change = 1 if rssi - previous_sighting.rssi > 0 else - 1
            avg_rssi = previous_sighting.rssi + step_change if abs(
                previous_sighting_rssi - rssi) > 15 else 0.6 * previous_sighting_rssi + 0.4 * rssi

            if ((beacon.type == 'M' and previous_sighting.detector == detector) or \
                    (detector.type == 'M' and previous_sighting.beacon == beacon)) and \
                            avg_rssi < detector.departure_rssi:
                logger.info('open_sighting() Closing previous related sighting \'%s\' as the rssi dropped below the ' + \
                            'departure_rssi configured for this detector (%s < %s).',
                            previous_sighting, avg_rssi, detector.departure_rssi)
                utils.close_sighting(previous_sighting, detector)
            elif ((beacon.type == 'M' and previous_sighting.detector != detector) or \
                    (detector.type == 'M' and previous_sighting.beacon != beacon)) and \
                            rssi * 1.05 > previous_sighting_rssi:
                logger.info('open_sighting() Closing previous related sighting \'%s\' as the device moved to another location.',
                    previous_sighting)
                utils.close_sighting(previous_sighting, detector)
            else:
                logger.debug('open_sighting() Updating previous related sighting \'%s\'.', previous_sighting)
                new_sighting = previous_sighting
                # TODO: metadata object should have separate properties for user defined / server util / app internal fields
                metadata_obj = json.loads(metadata)
                updated_metadata_obj = json.loads(new_sighting.metadata)
                for key, value in metadata_obj.items():
                    updated_metadata_obj[key] = value

                previous_sighting_occurred_at = previous_sighting.last_seen_at
                if not beacon.reported_missing or \
                                (now - previous_sighting_occurred_at).total_seconds() > REPORTED_MISSING_NOTIFICATION_EVERY_MINS * 60:
                    new_sighting.last_seen_at = None  # this forces the datetime update on the model save()

                new_sighting.rssi = avg_rssi
                new_sighting.detector_battery = detector_battery
                new_sighting.beacon_battery = beacon_battery
                new_sighting.location = location
                new_sighting.metadata = json.dumps(updated_metadata_obj)

                new_sighting.save()

        if beacon is not None and beacon.account_id != detector.account.id:
            if beacon.reported_missing:
                if (previous_sighting_occurred_at is None or
                            ( now - previous_sighting_occurred_at).total_seconds() > REPORTED_MISSING_NOTIFICATION_EVERY_MINS * 60):
                    logger.info('open_sighting() Reported missing beacon was seen at / by \'%s\'. ' +
                                'Notifying corresponding account owners...', detector)
                    try:
                        send_mail('Reported missing: {0}'.format(beacon.name),
                                  '{0} was seen near the following coordinates: {1}'.format(beacon.name,detector.location), settings.DEFAULT_FROM_EMAIL, [u.email for u in beacon.account.get_account_admins()])
                    except Exception as ex:
                        logger.exception('open_sighting() Failed to send reported missing email to account admins!')
                else:
                    logger.info('open_sighting() Reported missing beacon was seen at / by \'%s\'. ' + \
                                'Skipping notification as the last one was triggered less than 1 minute ago...', detector)
            else:
                logger.info('open_sighting() Ignoring current sighting as the beacon \'%s\' was seen at / by another account\'s ' +
                            'detector / user \'%s\' but has not been reported missing.', beacon, detector)
                return

        if new_sighting is None:
            if detector is not None and rssi < detector.arrival_rssi and \
                    (beacon.account_id == detector.account.id or not beacon.reported_missing):
                logger.info('open_sighting() Ignoring sighting of beacon \'%s\' at / by \'%s\' as the rssi is lower than the ' +
                            'arrival_rssi configured for this detector / user (%s < %s).', beacon, detector, rssi, detector.arrival_rssi)
            else:
                new_sighting = Sighting.objects.create(beacon=beacon, beacon_battery=beacon_battery, detector=detector, detector_battery=detector_battery,
                                                       location=location, rssi=rssi, metadata=metadata, type=type, is_active=(type != 'GPS'))

                logger.debug('open_sighting() Created new sighting \'%s\'.', new_sighting)

        if new_sighting is not None:
            utils.check_for_events_async(new_sighting, )

    def close_sighting_async(self, detector, detector_battery, beacon, beacon_battery, rssi, location, metadata):
        # check for events associated with this sighting in a different  thread
        t = threading.Thread(target=self.close_sighting, args=(detector, detector_battery, beacon, beacon_battery, rssi, location, metadata))
        t.start()

    def close_sighting(self, detector, detector_battery, beacon, beacon_battery, rssi, location, metadata):
        logger.debug('close_sighting() Started...')
        existing_sightings = Sighting.objects.filter(type='MC', is_active=True, beacon=beacon, detector=detector).order_by('-last_seen_at')[:1]
        if existing_sightings:
            existing_sighting = existing_sightings[0]
            existing_sighting.last_seen_at = None  # this forces the datetime update on the model save()
            existing_sighting.rssi = rssi
            existing_sighting.detector_battery = detector_battery
            existing_sighting.beacon_battery = beacon_battery
            existing_sighting.location = location

            metadata_obj = json.loads(metadata)
            existing_sighting_metadata = json.loads(existing_sighting.metadata)
            for key, value in metadata_obj.items():
                existing_sighting_metadata[key] = value
            existing_sighting.metadata = json.dumps(existing_sighting_metadata)

            utils.close_sighting(existing_sighting)


class AutoUpdateView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = json.loads(request.body.decode('utf-8'))

        company_id = data.get('company_id')
        detector_uid = data.get('detector_uid').lower()
        metadata = data.get('metadata', None)

        logger.info('AutoUpdateView.post() Auto update check from detector \'%s: %s\'', company_id, detector_uid)

        try:
            account = Account.objects.get(company_id=company_id)
        except Account.DoesNotExist:
            return utils.build_http_response('Invalid Company ID.', status.HTTP_400_BAD_REQUEST)

        try:
            detector = Detector.objects.get(uid=detector_uid)
            try:
                full_metadata = json.loads(detector.metadata)
            except Exception as ex:
                full_metadata = {}  # dict()
                full_metadata['auto_update'] = None
            full_metadata['device'] = json.loads(metadata)

            detector.metadata = json.dumps(full_metadata)
            detector.save()
        except Detector.DoesNotExist:
            full_metadata = {}  # dict()
            full_metadata['device'] = metadata
            full_metadata['auto_update'] = None
            Detector.objects.create(account=account, uid=detector_uid, metadata=json.dumps(full_metadata))

        # check for updates by comparing last_update_date in the metadata field
        if 'auto_update' in full_metadata and \
                full_metadata['auto_update'] and \
                        'date' in full_metadata['auto_update'] and \
                        full_metadata['device']['last_update_date'] < full_metadata['auto_update']['date']:
            return utils.build_http_response(full_metadata['auto_update'], status.HTTP_412_PRECONDITION_FAILED)

        return utils.build_http_response(None, status.HTTP_200_OK)


class LocalEventsView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        detector_uid = request.query_params.get('detector_uid').lower()

        logger.info('LocalEventView.get() Retrieving local events for detector \'%s\'', detector_uid)

        detectors = Detector.objects.filter(uid=detector_uid, is_active=True)

        if len(detectors) == 0:
            return utils.build_http_response('Invalid Detector UID or no active Detector found.', status.HTTP_400_BAD_REQUEST)

        events = Event.objects.filter(Q(is_active=True),
                                      Q(detectors=None) | Q(detectors__id__in=detectors.values_list('id', flat=True)))
        local_event_list = []
        if events is not None and len(events) > 0:
            for event in events:
                event_metadata = json.loads(event.metadata)
                is_local_event = event_metadata.get('event_is_local', False)
                if is_local_event:
                    event_dict = model_to_dict(event)

                    # Convert beacon IDs to UIDs (that's what the client knows)
                    if len(event_dict.get('unauthorized_beacons', [])) > 0:
                        event_dict['unauthorized_beacons'] = Beacon.objects.filter(is_active=True,
                                                                                   id__in=event_dict['unauthorized_beacons']).\
                                                                                    values_list('uid', flat=True)

                    # Convert beacon IDs to UIDs (that's what the client knows)
                    if len(event_dict.get('authorized_beacons', [])) > 0:
                        event_dict['authorized_beacons'] = Beacon.objects.filter(is_active=True,
                                                                                   id__in=event_dict['authorized_beacons']).\
                                                                                    values_list('uid', flat=True)

                    if 'detectors' in event_dict:
                        del event_dict['detectors']

                    local_event_list.append(event_dict)

        return utils.build_http_response(local_event_list, status.HTTP_200_OK)


class MakePaymentView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        data = json.loads(request.body.decode('utf-8'))

        now = datetime.now(timezone.utc)
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        license_about_to_expire = account.get_license_about_to_expire()
        license_due_for_payment = account.get_license_due_for_payment()
        if license_due_for_payment:
            license_metadata = json.loads(license_due_for_payment.metadata)

            license_due_for_payment.updated_by = request.user
            license_due_for_payment.reference_id = data.get('token_id', None)
            license_due_for_payment.valid_from = license_about_to_expire.valid_until if license_about_to_expire else now
            license_due_for_payment.valid_until = license_due_for_payment.valid_from + relativedelta(
                months=license_metadata['duration_in_months'])

            try:
                logger.debug('MakePaymentView.post() Charging %s%s on the card with token %s',license_due_for_payment.currency,
                             license_due_for_payment.amount, license_due_for_payment.reference_id)
                stripe.api_key = os.environ['STRIPE_SECRET_KEY']
                charge = stripe.Charge.create(
                    amount=license_due_for_payment.amount,
                    currency=license_due_for_payment.currency,
                    source=license_due_for_payment.reference_id,
                    description=license_due_for_payment.description,
                    receipt_email=data.get('receipt_email', None)
                )
                logger.info('MakePaymentView.post() Payment completed successfuly: %s', charge)
                license_due_for_payment.save()
            except stripe.error.CardError as ex:
                logger.exception('MakePaymentView.post() The card has been declined:')
                return Response(ex.message, status=status.HTTP_401_UNAUTHORIZED)

            serialized = LicenseSerializer(license_due_for_payment, context={'request': request})
            return utils.build_http_response(serialized.data, status.HTTP_200_OK)
        else:
            return utils.build_http_response('No payment is due...', status.HTTP_400_BAD_REQUEST)


class BeaconHistoryView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Sighting.objects.all()

    def get(self, request, format=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        if account:
            filter_beacon_id = request.query_params.get('beaconId', None)
            filter_timezone_offset = int(request.query_params.get('timezoneOffset', 0))
            filter_start_date = request.query_params.get('startDate', str(datetime.now(timezone.utc).date()) + 'T00:00:00')
            filter_start_date = str(datetime.strptime(filter_start_date, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=filter_timezone_offset)) + '+00'
            filter_end_date = request.query_params.get('endDate', str(datetime.now(timezone.utc).date()) + 'T23:59:59')
            filter_end_date = str(datetime.strptime(filter_end_date, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=filter_timezone_offset)) + '+00'

            if filter_beacon_id is None:
                queryset = self.queryset.filter(Q(first_seen_at__range=(filter_start_date, filter_end_date))) \
                    .order_by('-id')
            else:
                queryset = self.queryset.filter(
                    Q(beacon__uid=filter_beacon_id) | Q(beacon__reference_id=filter_beacon_id),
                    Q(first_seen_at__range=(filter_start_date, filter_end_date))) \
                    .order_by('-id')

            return utils.view_list(request, account, queryset, BeaconDetectorHistorySerializer, True)
        else:
            return utils.build_http_response('The current logged on user is not associated with any account.',
                                             status.HTTP_400_BAD_REQUEST)


class DetectorHistoryView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Sighting.objects.all()

    def get(self, request, format=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        if account:
            todayString = str(datetime.now(timezone.utc).date())
            filter_detector_id = request.query_params.get('detectorId', None)
            filter_timezone_offset = int(request.query_params.get('timezoneOffset', 0))
            filter_start_date = request.query_params.get('startDate', todayString + 'T00:00:00')
            filter_start_date = str(datetime.strptime(filter_start_date, '%Y-%m-%dT%H:%M:%S') + timedelta(
                    minutes=filter_timezone_offset)) + '+00'
            filter_end_date = request.query_params.get('endDate', todayString + 'T23:59:59')
            filter_end_date = str(datetime.strptime(filter_end_date, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=filter_timezone_offset)) + '+00'

            if filter_detector_id is None:
                queryset = self.queryset.filter(Q(first_seen_at__range=(filter_start_date, filter_end_date))) \
                    .order_by('-id')
            else:
                queryset = self.queryset.filter(Q(detector__uid=filter_detector_id) | Q(detector__reference_id=filter_detector_id),
                                                Q(first_seen_at__range=(filter_start_date, filter_end_date))) \
                                                .order_by('-id')

            return utils.view_list(request, account, queryset, DetectorBeaconHistorySerializer, True)
        else:
            return utils.build_http_response('The current logged on user is not associated with any account.',
                                             status.HTTP_400_BAD_REQUEST)
