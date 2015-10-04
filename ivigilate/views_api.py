import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework.response import Response
import stripe
from ivigilate.serializers import *
from rest_framework import permissions, viewsets, status, views, mixins
from ivigilate import utils
from dateutil.relativedelta import relativedelta
import datetime, pytz, json, logging

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
                if metadata is not None and len(metadata.strip()) > 0:
                    now = datetime.datetime.now(timezone.utc)
                    metadata = json.loads(metadata)
                    metadata['device']['last_login_date'] = now.strftime('%Y-%m-%d %H:%M')
                    if user.metadata is not None and len(user.metadata.strip()) > 0:
                        user_metadata = json.loads(user.metadata)
                        existing_device = next((device for device in user_metadata['devices'] if device['imei'] == metadata['device']['imei']), None)
                        if existing_device is not None:
                            existing_device['last_login_date'] = now.strftime('%Y-%m-%d %H:%M')
                    else:
                        user_metadata = {}
                        user_metadata['devices'] = []
                        user_metadata['devices'].append(metadata['device'])

                    user.metadata = json.dumps(user_metadata)
                    user.save()

                    try:
                        Detector.objects.get(uid=user.email)
                    except Detector.DoesNotExist:
                        Detector.objects.create(account=user.account,uid=user.email,reference_id=user.email,
                                                name=user.get_full_name(), type='U')

                serialized = AuthUserReadSerializer(user, context={'request': request})
                return Response(serialized.data, status=status.HTTP_200_OK)
            else:
                return Response('This user has been disabled.', status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response('Invalid email/password combination.', status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class AddSightingsView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        REPORTED_MISSING_NOTIFICATION_EVERY_MINS = 1
        data = json.loads(request.body.decode('utf-8'))

        if (data is not None and len(data) > 0):
            logger.info('Got %s sightings', len(data))
            for sighting in data:
                company_id = sighting.get('company_id')
                beacon_uid = sighting.get('beacon_uid', None)
                detector_uid = sighting.get('detector_uid').lower()
                rssi = sighting.get('rssi', None)
                battery = sighting.get('battery', None)
                location = sighting.get('location', None)

                try:
                    account = Account.objects.get(company_id=company_id)
                    if account.get_license_in_force() is None:
                        return Response('Ignoring sighting as the Account doesn\'t have a valid subscription.',
                                        status=status.HTTP_412_PRECONDITION_FAILED)
                except Account.DoesNotExist:
                    logger.warning('Attempt to add a sighting for an invalid Company ID.')
                    return Response('Invalid Company ID.', status=status.HTTP_400_BAD_REQUEST)

                try:
                    beacon = Beacon.objects.get(uid=beacon_uid)
                    if not beacon.is_active:
                        return Response('Ignoring sighting as the Beacon is not active on the system.',
                                        status=status.HTTP_412_PRECONDITION_FAILED)
                except Beacon.DoesNotExist:
                    beacon = Beacon.objects.create(account=account, uid=beacon_uid)

                try:
                    detector = Detector.objects.get(uid=detector_uid)
                    if not detector.is_active:
                        return Response('Ignoring sighting as the Detector is not active on the system.',
                                        status=status.HTTP_412_PRECONDITION_FAILED)
                    elif location is not None:
                        location = json.dumps(location)
                    else:
                        location = detector.location
                except Detector.DoesNotExist:
                    return Response('Invalid Detector UID (couldn\'t find corresponding detector).',
                                    status=status.HTTP_400_BAD_REQUEST)

                now = datetime.datetime.now(timezone.utc)
                previous_sightings = Sighting.objects.filter(is_current=True, beacon=beacon).order_by('-last_seen_at')[:1]
                previous_sighting_occurred_at = None
                new_sighting = None
                if previous_sightings:
                    previous_sighting = previous_sightings[0]
                    if detector is not None and rssi < detector.departure_rssi:
                        logger.info('Closing previous related sighting \'%s\' as the rssi dropped below the ' + \
                                    'departure_rssi configured for this detector (%s < %s).',
                                    previous_sighting, rssi, detector.departure_rssi)
                        utils.close_sighting(previous_sighting, detector)
                    elif previous_sighting.detector != detector and rssi > (previous_sighting.rssi if previous_sighting.rssi is not None else 0):
                        logger.info('Closing previous related sighting \'%s\' as the beacon moved to another location.',
                                    previous_sighting)
                        utils.close_sighting(previous_sighting, detector)
                    else:
                        logger.debug('Updating previous related sighting \'%s\'.', previous_sighting)
                        new_sighting = previous_sighting
                        previous_sighting_occurred_at = previous_sighting.last_seen_at
                        if not beacon.reported_missing or \
                            (now - previous_sighting_occurred_at).total_seconds() > REPORTED_MISSING_NOTIFICATION_EVERY_MINS * 60:
                            new_sighting.last_seen_at = None  # this forces the datetime update on the model save()
                        new_sighting.rssi = rssi
                        new_sighting.battery = battery
                        new_sighting.location = location
                        new_sighting.save()

                if beacon.account_id != account.id:
                    if beacon.reported_missing:
                        if (previous_sighting_occurred_at is None or
                            (now - previous_sighting_occurred_at).total_seconds() > REPORTED_MISSING_NOTIFICATION_EVERY_MINS * 60):
                            logger.info('Reported missing beacon was seen at / by \'%s\'. ' +
                                        'Notifying corresponding account owners...', detector)
                            try:
                                send_mail('Reported missing: {0}'.format(beacon.name),
                                          '{0} was seen near the following coordinates: {1}'.format(beacon.name, detector.location),
                                          settings.DEFAULT_FROM_EMAIL,
                                          [u.email for u in beacon.account.get_account_admins()])
                            except Exception as ex:
                                logger.exception('Failed to send reported missing email to account admins!')
                        else:
                            logger.info('Reported missing beacon was seen at / by \'%s\'. ' + \
                                        'Skipping notification as the last one was triggered less than 1 minute ago...', detector)
                            return Response('Ignored sighting as the beacon doesn\'t belong to this account.')
                    else:
                        logger.info('Ignoring current sighting as the beacon \'%s\' was seen at / by another account\'s ' +
                                    'detector / user \'%s\' but has not been reported missing.', beacon, detector)
                        return Response('Ignored sighting as the beacon doesn\'t belong to this account.')

                if new_sighting is None:
                    if detector is not None and rssi < detector.arrival_rssi and \
                            (beacon.account_id == account.id or not beacon.reported_missing):
                        logger.info('Ignoring sighting of beacon \'%s\' at / by \'%s\' as the rssi is lower than the ' +
                                    'arrival_rssi configured for this detector / user (%s < %s).', beacon, detector, rssi, detector.arrival_rssi)
                        return Response('Ignored sighting due to weak rssi.')
                    else:
                        new_sighting = Sighting.objects.create(beacon=beacon, detector=detector,
                                                               location=location, rssi=rssi, battery=battery)
                        logger.debug('Created new sighting \'%s\'.', new_sighting)

                # check for events associated with this sighting in a different  thread
                t = threading.Thread(target=utils.check_for_events, args=(sighting,))
                t.start()

        # serialized = SightingReadSerializer(new_sighting, context={'request': request})
        # return Response(serialized.data)
        return Response(status=status.HTTP_200_OK)


class AutoUpdateView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = json.loads(request.body.decode('utf-8'))

        company_id = data.get('company_id')
        detector_uid = data.get('detector_uid').lower()
        metadata = data.get('metadata', None)

        try:
            account = Account.objects.get(company_id=company_id)
        except Account.DoesNotExist:
            return Response('Invalid Company ID.', status=status.HTTP_400_BAD_REQUEST)

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
            Detector.objects.create(account=account,uid=detector_uid,metadata=json.dumps(full_metadata))

        # check for updates by comparing last_update_date in the metadata field
        if 'auto_update' in full_metadata and \
                full_metadata['auto_update'] and \
                        'date' in full_metadata['auto_update'] and \
                        full_metadata['device']['last_update_date'] < full_metadata['auto_update']['date']:
            return Response(full_metadata['auto_update'], status=status.HTTP_412_PRECONDITION_FAILED)

        return Response(status=status.HTTP_200_OK)


class MakePaymentView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, format=None):
        data = json.loads(request.body.decode('utf-8'))

        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        license_about_to_expire = account.get_license_about_to_expire()
        license_due_for_payment = account.get_license_due_for_payment()
        if license_due_for_payment:
            license_metadata = json.loads(license_due_for_payment.metadata)

            license_due_for_payment.reference_id = data.get('token_id', None)
            license_due_for_payment.valid_from = datetime.datetime.combine(
                                                    license_about_to_expire.valid_until.date() + relativedelta(days=1) \
                                                    if license_about_to_expire else datetime.datetime.now(timezone.utc).date(),
                                                    datetime.time(0, 0, 0, tzinfo=pytz.UTC))
            license_due_for_payment.valid_until = datetime.datetime.combine(
                                                    license_due_for_payment.valid_from +
                                                    relativedelta(months=license_metadata['duration_in_months']),
                                                    datetime.time(23, 59, 59, tzinfo=pytz.UTC))

            try:
                logger.debug('Charging %s%s on the card with token %s', license_due_for_payment.currency,
                             license_due_for_payment.amount, license_due_for_payment.reference_id)
                stripe.api_key = os.environ['STRIPE_SECRET_KEY']
                charge = stripe.Charge.create(
                    amount=license_due_for_payment.amount,
                    currency=license_due_for_payment.currency,
                    source=license_due_for_payment.reference_id,
                    description=license_due_for_payment.description,
                    receipt_email=data.get('receipt_email', None)
                )
                logger.info('Payment completed successfuly: %s', charge)
                license_due_for_payment.save()
            except stripe.error.CardError as ex:
                logger.exception('The card has been declined:')
                return Response(ex.message, status=status.HTTP_401_UNAUTHORIZED)

            serialized = LicenseSerializer(license_due_for_payment, context={'request': request})
            return Response(serialized.data)
        else:
            return Response('No payment is due...', status=status.HTTP_400_BAD_REQUEST)

