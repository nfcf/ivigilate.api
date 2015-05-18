from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from rest_framework.response import Response
from ivigilate.serializers import *
from rest_framework import permissions, viewsets, status, mixins
from ivigilate import utils
import json, logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(), )
        return (permissions.IsAuthenticated(), )

    def list(self, request):
        if request.user and request.user.is_staff:
            # return only the list of active accounts
            queryset = self.queryset.filter(Q(licenses__valid_until=None) | Q(licenses__valid_until__gt=datetime.now(timezone.utc))).distinct()
            page = self.paginate_queryset(queryset)
            serializer = self.get_pagination_serializer(page)
            return Response(serializer.data)
        else:
            logger.critical('The user \'%s\' tried to access the accounts list without admin permissions.',
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
            return (permissions.AllowAny(), )
        return (permissions.IsAuthenticated(), )

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        if not isinstance(request.user, AnonymousUser) and account == None:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(account=account)
        page = self.paginate_queryset(queryset)
        serializer = self.get_pagination_serializer(page)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        error_message = None

        password = request.data.get('password', None)
        if password is None:
            error_message = "Password cannot be left empty."
        elif serializer.is_valid():
            if serializer.save():
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        if error_message is None:
            error_message = serializer.errors

        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)


class PlaceViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin,
                   mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Place.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PlaceReadSerializer
        return PlaceWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(), )
        return (permissions.IsAuthenticated(), )

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(account=account)
        return utils.view_list(request, account, queryset, self.get_serializer_class())

    def retrieve(self, request, pk=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=pk, account=account)
        except Place.DoesNotExist:
            return Response('Place does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            instance = self.queryset.get(id=pk, account=account)
        except Place.DoesNotExist:
            return Response('Place does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            if serializer.save(user=user):
                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovableViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Movable.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MovableReadSerializer
        return MovableWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(), )
        return (permissions.IsAuthenticated(), )

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(account=account)
        return utils.view_list(request, account, queryset, self.get_serializer_class())

    def retrieve(self, request, pk=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=pk, account=account)
        except Movable.DoesNotExist:
            return Response('Movable does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        instance = self.queryset.get(id=pk)
        # if self.request.FILES.get('file'):
        # instance.photo = self.request.FILES.get('file')

        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            if serializer.save(user=user):
                # work around to handle the M2M field as DRF doesn't handle them well...
                events = self.request.DATA.get('events', None)
                if events:
                    movable = Movable.objects.get(uid=serializer.validated_data['uid'])

                    new_list = events
                    old_list = movable.events.all().values_list('id', flat=True)
                    to_add_list = list(set(new_list) - set(old_list))
                    to_remove_list = list(set(old_list) - set(new_list))
                    for id in to_add_list:
                        movable.events.add(id)
                    for id in to_remove_list:
                        movable.events.remove(id)
                # delete this field from the response as it isn't serializable
                if 'photo' in serializer.validated_data:
                    del serializer.validated_data['photo']
                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SightingViewSet(viewsets.ModelViewSet):
    queryset = Sighting.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SightingReadSerializer
        return SightingWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS']:
            return (permissions.AllowAny(), )
        return (permissions.IsAuthenticated(), )

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        if account:
            filter_date = str(datetime.now(timezone.utc).date())
            filter_places = []
            filter_show_all = False
            if request.query_params is not None:
                if request.query_params.get('filterDate') is not None:
                    filter_date = request.query_params.get('filterDate')
                if request.query_params.get('filterPlaces') is not None:
                    filter_places = request.query_params.getlist('filterPlaces')
                if request.query_params.get('filterShowAll') is not None:
                    filter_show_all = request.query_params.get('filterShowAll') in ['True', 'true', '1']

            filteredQuery = 'SELECT s.* ' + \
                            'FROM ivigilate_sighting s JOIN ivigilate_movable m ON s.movable_id = m.id ' + \
                            'WHERE m.account_id = %s AND s.last_seen_at BETWEEN %s AND %s ' + \
                            'AND (%s OR s.place_id = ANY(%s::integer[])) AND s.last_seen_at IN (' + \
                            ' SELECT MAX(last_seen_at) FROM ivigilate_sighting GROUP BY movable_id' + \
                            ') ORDER BY s.last_seen_at DESC'
            filteredQueryParams = [account.id, filter_date + ' 00:00:00', filter_date + ' 23:59:59',
                                   len(filter_places) == 0, [int(p) for p in filter_places]]

            showAllQuery = '(SELECT s.* ' + \
                           'FROM ivigilate_sighting s JOIN ivigilate_movable m ON s.movable_id = m.id ' + \
                           'WHERE m.account_id = %s AND s.first_seen_at >= %s AND s.last_seen_at <= %s ' + \
                           'AND (%s OR s.place_id = ANY(%s)) AND s.last_seen_at IN (' + \
                           ' SELECT MAX(last_seen_at) FROM ivigilate_sighting GROUP BY movable_id' + \
                           ') ORDER BY s.last_seen_at DESC)' + \
                           ' UNION ' + \
                           '(SELECT s.* ' + \
                           'FROM ivigilate_sighting s JOIN ivigilate_movable m ON s.movable_id = m.id ' + \
                           'WHERE m.account_id = %s AND s.last_seen_at <= %s ' + \
                           'AND s.last_seen_at IN (' + \
                           ' SELECT MAX(last_seen_at) FROM ivigilate_sighting GROUP BY movable_id' + \
                           ') ORDER BY s.last_seen_at DESC)'
            showAllQueryParams = [account.id, filter_date + ' 00:00:00', filter_date + ' 23:59:59',
                                  len(filter_places) == 0, [int(p) for p in filter_places],
                                  account.id, filter_date + ' 23:59:59']

            queryset = self.queryset.raw(showAllQuery if filter_show_all else filteredQuery,
                                         showAllQueryParams if filter_show_all else filteredQueryParams)
            # print(queryset.query)
            return utils.view_list(request, account, queryset, self.get_serializer_class())
        else:
            return Response('The current logged on user is not associated with any account.',
                            status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=pk, movable__account=account)
        except Sighting.DoesNotExist:
            return Response('Sighting does not exist or is not associated with the current logged on account.',
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        serializer = self.get_serializer_class()(data=request.data)

        if serializer.is_valid():
            if serializer.save(user=user):
                # remove fields from the response as they aren't serializable nor needed
                if 'movable' in serializer.validated_data:
                    del serializer.validated_data['movable']
                if 'place' in serializer.validated_data:
                    del serializer.validated_data['place']
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        instance = self.queryset.get(id=pk)
        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            if serializer.save(user=user):
                # remove fields from the response as they aren't serializable nor needed
                if 'movable' in serializer.validated_data:
                    del serializer.validated_data['movable']
                if 'place' in serializer.validated_data:
                    del serializer.validated_data['place']
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
            return (permissions.AllowAny(), )
        return (permissions.IsAuthenticated(), )

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

    def add_m2m_fields(self, event, movables, places):
        # work around to handle the M2M field as DRF doesn't handle them well...
        movables = self.request.DATA.get('movables', None)
        if movables:
            new_list = movables
            old_list = event.movables.all().values_list('id', flat=True)
            to_add_list = list(set(new_list) - set(old_list))
            to_remove_list = list(set(old_list) - set(new_list))
            for id in to_add_list:
                event.movables.add(id)
            for id in to_remove_list:
                event.movables.remove(id)
        # work around to handle the M2M field as DRF doesn't handle them well...
        places = self.request.DATA.get('places', None)
        if places:
            new_list = places
            old_list = event.places.all().values_list('id', flat=True)
            to_add_list = list(set(new_list) - set(old_list))
            to_remove_list = list(set(old_list) - set(new_list))
            for id in to_add_list:
                event.places.add(id)
            for id in to_remove_list:
                event.places.remove(id)


    def create(self, request):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        serializer = self.get_serializer_class()(data=request.data)

        if serializer.is_valid():
            if serializer.save(updated_by=user, account=account):
                event = Event.objects.get(reference_id=serializer.validated_data['reference_id'])
                movables = self.request.DATA.get('movables', None)
                places = self.request.DATA.get('places', None)
                self.add_m2m_fields(event, movables, places)

                # remove fields from the response as they aren't serializable nor needed
                if 'sighting_previous_event' in serializer.validated_data:
                    del serializer.validated_data['sighting_previous_event']

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
            if serializer.save(updated_by=user):
                event = Event.objects.get(reference_id=serializer.validated_data['reference_id'])
                movables = self.request.DATA.get('movables', None)
                places = self.request.DATA.get('places', None)
                self.add_m2m_fields(event, movables, places)

                # remove fields from the response as they aren't serializable nor needed
                if 'sighting_previous_event' in serializer.validated_data:
                    del serializer.validated_data['sighting_previous_event']

                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


