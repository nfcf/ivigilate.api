import logging
import threading

from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import Q
from rest_framework import permissions, viewsets, status, mixins
from rest_framework.response import Response

from ivigilate import utils
from ivigilate.serializers import *

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def list(self, request):
        if request.user and request.user.is_staff:
            # return only the list of active accounts
            queryset = self.queryset.filter(
                Q(licenses__valid_until=None) | Q(licenses__valid_until__gt=datetime.now(timezone.utc))).distinct()
            return utils.view_list(request, None, queryset, self.get_serializer_class())
        else:
            logger.critical(
                'AccountViewSet.list() The user \'%s\' tried to access the accounts list without admin permissions.',
                request.user)
            return Response('You do not have permissions to access this list.',
                            status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        if account.id == int(pk):
            try:
                queryset = self.queryset.get(id=pk)
            except Account.DoesNotExist:
                return Response('Account does not exist.',
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(queryset, many=False, context={'request': request})
            return Response(serializer.data)
        else:
            return Response('You do not have permissions to access this account information.',
                            status=status.HTTP_400_BAD_REQUEST)


class AuthUserViewSet(viewsets.ModelViewSet):
    queryset = AuthUser.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AuthUserReadSerializer
        return AuthUserWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS', 'POST']:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        if not isinstance(request.user, AnonymousUser) and account == None:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(account=account)
        return utils.view_list(request, account, queryset, self.get_serializer_class())

    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        error_message = None

        password = request.data.get('password', None)
        if password is None:
            error_message = "Password cannot be left empty."
        elif serializer.is_valid():
            account = Account.objects.get(company_id=request.data['company_id'])
            if serializer.save(account=account):
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        if error_message is None:
            error_message = serializer.errors

        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            instance = self.queryset.get(id=pk, account=account)
            original_email = instance.email
        except AuthUser.DoesNotExist:
            return Response('User does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            if serializer.save():
                user = instance
                if instance.email != original_email:
                    password = serializer.validated_data.get('password')
                    if password is not None:
                        logout(request)
                        user = authenticate(email=instance.email, password=password)
                        if user is not None:
                            login(request, user)
                    try:
                        detector = Detector.objects.get(uid=original_email)
                        detector.uid = user.email
                        detector.save()
                    except Detector.DoesNotExist:
                        pass
                else:
                    update_session_auth_hash(request, user)

                return Response(AuthUserReadSerializer(user, context={'request': request}).data,
                                status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetectorViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin,
                      mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Detector.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DetectorReadSerializer
        return DetectorWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(account=account)

        #Temporary update required for regression (due to removing the 'User' detector type
        with transaction.atomic():
            for detector in queryset:
                type = 'F' if detector.type == 'F' else 'M'
                Detector.objects.filter(pk=detector.pk).update(type=type)

        return utils.view_list(request, account, queryset, self.get_serializer_class())

    def retrieve(self, request, pk=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=pk, account=account)
        except Detector.DoesNotExist:
            return Response('Detector does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None

        try:
            if account:
                serializer = self.get_serializer_class()(data=request.data)
                if serializer.is_valid():
                    if serializer.save(updated_by=user, account=account):
                        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('The current logged on user is not associated with any account.',
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception('Failed to create Detector with error:')
            return Response('Failed to create Detector.',
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            instance = self.queryset.get(id=pk, account=account)
        except Detector.DoesNotExist:
            return Response('Detector does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            if serializer.save(user=user):
                # delete this field from the response as it isn't serializable
                if 'photo' in serializer.validated_data:
                    del serializer.validated_data['photo']
                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BeaconViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin,
                    mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Beacon.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BeaconReadSerializer
        return BeaconWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(account=account)
        return utils.view_list(request, account, queryset, self.get_serializer_class())

    def retrieve(self, request, pk=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=pk, account=account)
        except Beacon.DoesNotExist:
            return Response('Beacon does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None

        try:
            if account:
                serializer = self.get_serializer_class()(data=request.data)
                if serializer.is_valid():
                    if serializer.save(updated_by=user, account=account):
                        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('The current logged on user is not associated with any account.',
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception('Failed to create Beacon with error:')
            return Response('Failed to create Beacon.',
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        instance = self.queryset.get(id=pk)
        # if self.request.FILES.get('file'):
        # instance.photo = self.request.FILES.get('file')

        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            beacon = serializer.save(user=user)
            if beacon:
                unauthorized_events = self.request.DATA.get('unauthorized_events', None)
                self.update_m2m_fields(beacon, unauthorized_events)

                # delete this field from the response as it isn't serializable
                if 'photo' in serializer.validated_data:
                    del serializer.validated_data['photo']
                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_m2m_fields(self, beacon, unauthorized_events):
        # work around to handle the M2M field as DRF doesn't handle them well...
        if isinstance(unauthorized_events, list):
            new_list = unauthorized_events
            old_list = beacon.unauthorized_events.all().values_list('id', flat=True)
            to_add_list = list(set(new_list) - set(old_list))
            to_remove_list = list(set(old_list) - set(new_list))
            for id in to_add_list:
                beacon.unauthorized_events.add(id)
            for id in to_remove_list:
                beacon.unauthorized_events.remove(id)


class SightingViewSet(viewsets.ModelViewSet):
    queryset = Sighting.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SightingReadSerializer
        return SightingWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def list(self, request):

        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        if account:

            filter_beacon_id = request.query_params.get('beaconId', None)
            filter_detector_id = request.query_params.get('detectorId', None)
            filter_timezone_offset = int(request.query_params.get('timezoneOffset', 0))
            filter_start_date = request.query_params.get('startDate',
                                                         str(datetime.now(timezone.utc).date()))
            filter_start_date = str(
                datetime.strptime(filter_start_date, '%Y-%m-%dT%H:%M:%S') + timedelta(
                    minutes=filter_timezone_offset)) + '+00'
            filter_end_date = request.query_params.get('endDate',
                                                       str(datetime.now(timezone.utc).date()) + 'T23:59:59')
            filter_end_date = str(
                datetime.strptime(filter_end_date, '%Y-%m-%dT%H:%M:%S') + timedelta(
                    minutes=filter_timezone_offset)) + '+00'

            if filter_beacon_id is None and filter_detector_id is None:
                queryset = self.queryset.filter(
                    Q(beacon=None) | Q(beacon__account=account), Q(detector__account=account),
                    Q(first_seen_at__range=(filter_start_date, filter_end_date)),
                    Q(beacon=None) | Q(beacon__is_active=True), Q(detector__is_active=True)) \
                    .order_by('-id')
            elif filter_beacon_id:
                queryset = self.queryset.filter(
                    Q(beacon__account=account), Q(detector__account=account),
                    Q(beacon__uid=filter_beacon_id) | Q(beacon__reference_id=filter_beacon_id),
                    Q(first_seen_at__range=(filter_start_date, filter_end_date)),
                    Q(beacon__is_active=True), Q(detector__is_active=True))
            else:
                queryset = self.queryset.filter(
                    Q(beacon=None) | Q(beacon__account=account), Q(detector__account=account),
                    Q(detector__uid=filter_detector_id) | Q(detector__reference_id=filter_detector_id),
                    Q(first_seen_at__range=(filter_start_date, filter_end_date)),
                    Q(beacon=None) | Q(beacon__is_active=True), Q(detector__is_active=True)) \
                    .order_by('-id')

            return utils.view_list(request, account, queryset, SightingHistorySerializer, True)
        else:
            return utils.build_http_response('The current logged on user is not associated with any account.',
                                             status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=pk, beacon__account=account)
        except Sighting.DoesNotExist:
            return Response('Sighting does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        serializer = self.get_serializer_class()(data=request.data)

        if serializer.is_valid():
            sighting = serializer.save(user=user)
            if sighting:
                utils.check_for_events_async(sighting)

                # remove fields from the response as they aren't serializable nor needed
                if 'beacon' in serializer.validated_data:
                    del serializer.validated_data['beacon']
                if 'detector' in serializer.validated_data:
                    del serializer.validated_data['detector']
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        instance = self.queryset.get(id=pk)
        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            sighting = serializer.save(user=user)
            if sighting:
                utils.check_for_events_async(sighting)

                # remove fields from the response as they aren't serializable nor needed
                if 'beacon' in serializer.validated_data:
                    del serializer.validated_data['beacon']
                if 'detector' in serializer.validated_data:
                    del serializer.validated_data['detector']
                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EventReadSerializer
        return EventWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(account=account)
        return utils.view_list(request, account, queryset, self.get_serializer_class())

    def retrieve(self, request, pk=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=pk, account=account)
        except Event.DoesNotExist:
            return Response('Event does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        serializer = self.get_serializer_class()(data=request.data)

        if serializer.is_valid():
            event = serializer.save(updated_by=user, account=account)
            if event:
                unauthorized_beacons = self.request.DATA.get('unauthorized_beacons', None)
                authorized_beacons = self.request.DATA.get('authorized_beacons', None)
                detectors = self.request.DATA.get('detectors', None)
                self.update_m2m_fields(event, unauthorized_beacons, authorized_beacons, detectors)

                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            instance = self.queryset.get(id=pk, account=account)
        except Event.DoesNotExist:
            return Response('Event does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            event = serializer.save(updated_by=user)
            if event:
                unauthorized_beacons = self.request.DATA.get('unauthorized_beacons', None)
                authorized_beacons = self.request.DATA.get('authorized_beacons', None)
                detectors = self.request.DATA.get('detectors', None)
                self.update_m2m_fields(event, unauthorized_beacons, authorized_beacons, detectors)

                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_m2m_fields(self, event, unauthorized_beacons, authorized_beacons, detectors):
        # work around to handle the M2M field as DRF doesn't handle them well...
        if isinstance(unauthorized_beacons, list):
            new_list = unauthorized_beacons
            old_list = event.unauthorized_beacons.all().values_list('id', flat=True)
            to_add_list = list(set(new_list) - set(old_list))
            to_remove_list = list(set(old_list) - set(new_list))
            for id in to_add_list:
                event.unauthorized_beacons.add(id)
            for id in to_remove_list:
                event.unauthorized_beacons.remove(id)

        # work around to handle the M2M field as DRF doesn't handle them well...
        if isinstance(authorized_beacons, list):
            new_list = authorized_beacons
            old_list = event.authorized_beacons.all().values_list('id', flat=True)
            to_add_list = list(set(new_list) - set(old_list))
            to_remove_list = list(set(old_list) - set(new_list))
            for id in to_add_list:
                event.authorized_beacons.add(id)
            for id in to_remove_list:
                event.authorized_beacons.remove(id)

        # work around to handle the M2M field as DRF doesn't handle them well...
        if isinstance(detectors, list):
            new_list = detectors
            old_list = event.detectors.all().values_list('id', flat=True)
            to_add_list = list(set(new_list) - set(old_list))
            to_remove_list = list(set(old_list) - set(new_list))
            for id in to_add_list:
                event.detectors.add(id)
            for id in to_remove_list:
                event.detectors.remove(id)


class LimitViewSet(viewsets.ModelViewSet):
    queryset = Limit.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LimitReadSerializer
        return LimitWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(account=account)
        return utils.view_list(request, account, queryset, self.get_serializer_class())

    def retrieve(self, request, pk=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=pk, account=account)
        except Limit.DoesNotExist:
            return Response('Limit does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        serializer = self.get_serializer_class()(data=request.data)

        if serializer.is_valid():
            limit = serializer.save(updated_by=user, account=account)
            if limit:
                events = self.request.DATA.get('events', None)
                beacons = self.request.DATA.get('beacons', None)
                self.update_m2m_fields(limit, events, beacons)

                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            instance = self.queryset.get(id=pk, account=account)
        except Limit.DoesNotExist:
            return Response('Limit does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            limit = serializer.save(updated_by=user)
            if limit:
                events = self.request.DATA.get('events', None)
                beacons = self.request.DATA.get('beacons', None)
                self.update_m2m_fields(limit, events, beacons)

                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_m2m_fields(self, limit, events, beacons):
        # work around to handle the M2M field as DRF doesn't handle them well...
        if isinstance(events, list):
            new_list = events
            old_list = limit.events.all().values_list('id', flat=True)
            to_add_list = list(set(new_list) - set(old_list))
            to_remove_list = list(set(old_list) - set(new_list))
            for id in to_add_list:
                limit.events.add(id)
            for id in to_remove_list:
                limit.events.remove(id)

        if isinstance(beacons, list):
            new_list = beacons
            old_list = limit.beacons.all().values_list('id', flat=True)
            to_add_list = list(set(new_list) - set(old_list))
            to_remove_list = list(set(old_list) - set(new_list))
            for id in to_add_list:
                limit.beacons.add(id)
            for id in to_remove_list:
                limit.beacons.remove(id)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        if account:
            queryset = self.queryset.filter(account=account, is_active=True)
            return utils.view_list(request, account, queryset, self.get_serializer_class())
        else:
            return Response('The current logged on user is not associated with any account.',
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            instance = self.queryset.get(id=pk, account=account)
        except Notification.DoesNotExist:
            return Response('Notification does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            serializer.save(updated_by=user)

            return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
