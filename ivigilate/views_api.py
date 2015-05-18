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
import json, logging

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

        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                serialized = AuthUserReadSerializer(user, context={'request': request})
                return Response(serialized.data)
            else:
                return Response('This user has been disabled.',
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response('Email/password combination invalid.',
                            status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class AddSightingView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = json.loads(request.body.decode('utf-8'))

        company_id = data.get('company_id', None)
        watcher_uid = data.get('watcher_uid', None)
        place = None
        user = None
        movable_uid = data.get('movable_uid', None)
        rssi = data.get('rssi', None)
        battery = data.get('battery', None)

        try:
            account = Account.objects.get(company_id=company_id)
        except Account.DoesNotExist:
            return Response('Invalid Company ID.', status=status.HTTP_400_BAD_REQUEST)

        try:
            movable = Movable.objects.get(uid=movable_uid)
        except Movable.DoesNotExist:
            movable = Movable.objects.create(account=account, uid=movable_uid)

        if '@' in watcher_uid:
            try:
                user = AuthUser.objects.get(email=watcher_uid)
            except AuthUser.DoesNotExist:
                return Response('Invalid Watcher UID (couldn\'t find corresponding user).',
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                place = Place.objects.get(uid=watcher_uid)
            except Place.DoesNotExist:
                return Response('Invalid Watcher UID (couldn\'t find corresponding place).',
                                status=status.HTTP_400_BAD_REQUEST)

        if movable.account != account:
            if movable.reported_missing:
                dummy = 2  # do something...
            else:
                return Response('Ignored sighting as the movable doesn\'t belong to this account.')

        previous_sightings = Sighting.objects.filter(is_current=True, movable=movable).order_by('-last_seen_at')[:1]
        new_sighting = None
        if previous_sightings:
            previous_sighting = previous_sightings[0]
            if (previous_sighting.place == place and previous_sighting.user == user) or \
                    ((previous_sighting.place != place or previous_sighting.user != user) and
                             previous_sighting.rssi >= rssi):
                logger.debug('Updating previous sighting \'%s\' as the movable didn\'t change places.',
                             previous_sighting)
                new_sighting = previous_sighting
                new_sighting.last_seen_at = None  # this forces the datetime update
                new_sighting.rssi = rssi
                new_sighting.battery = battery
                new_sighting.save()
            else:  # if (previous_sighting.place != place or previous_sighting.user != user) and previous_sighting.rssi < rssi:
                utils.close_sighting(previous_sighting, place, user)

        if not new_sighting:
            # check if belongs to account
            new_sighting = Sighting.objects.create(movable=movable, place=place, user=user, rssi=rssi, battery=battery)
            logger.debug('Created new sighting \'%s\'.', new_sighting)

        utils.check_for_events(new_sighting)

        serialized = SightingReadSerializer(new_sighting, context={'request': request})
        return Response(serialized.data)


class AutoUpdateView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = json.loads(request.body.decode('utf-8'))

        company_id = data.get('company_id', None)
        watcher_uid = data.get('watcher_uid', None)
        metadata = data.get('metadata', None)

        try:
            account = Account.objects.get(company_id=company_id)
        except Account.DoesNotExist:
            return Response('Invalid Company ID.', status=status.HTTP_400_BAD_REQUEST)

        try:
            place = Place.objects.get(uid=watcher_uid)
            try:
                full_metadata = json.loads(place.metadata)
            except Exception as ex:
                full_metadata = dict()
                full_metadata['auto_update'] = None
            full_metadata['device'] = json.loads(metadata)

            place.metadata = json.dumps(full_metadata)
            place.save()
        except Place.DoesNotExist:
            full_metadata = dict()
            full_metadata['device'] = metadata
            full_metadata['auto_update'] = None
            Place.objects.create(account=account,
                                 uid=watcher_uid,
                                 metadata=json.dumps(full_metadata))

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
            license_due_for_payment.valid_from = license_about_to_expire.valid_until if license_about_to_expire else datetime.now(timezone.utc)
            license_due_for_payment.valid_until = license_due_for_payment.valid_from + relativedelta(months=license_metadata['duration_in_months'])

            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                logger.debug('Charging %s%s on the card with token %s', license_due_for_payment.currency,
                             license_due_for_payment.amount, license_due_for_payment.reference_id)
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

