from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from ivigilate.serializers import *
from ivigilate.permissions import IsAccountOwner
from rest_framework import permissions, viewsets, status, views
from django.shortcuts import get_object_or_404
import json
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class IndexView(TemplateView):
    template_name = 'index.html'

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)


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
            queryset = self.queryset.filter(licenses__valid_until__gt=datetime.now(timezone.utc)).distinct()
            page = self.paginate_queryset(queryset)
            serializer = self.get_pagination_serializer(page)
            return Response(serializer.data)
        else:
            logger.critical('The user \'%s\' tried to access the accounts list without admin permissions.', request.user)
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


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PlaceReadSerializer
        return PlaceWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS', 'POST']:
            return (permissions.AllowAny(), )
        return (permissions.IsAuthenticated(), )

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(account=account)
        # page = self.paginate_queryset(queryset)
        # serializer = self.get_pagination_serializer(page)
        serializer = self.get_serializer_class()(queryset, many=True, context={'request': request})
        return Response(serializer.data)

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
        instance = self.queryset.get(id=pk)
        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            if serializer.save(user=user):
                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovableViewSet(viewsets.ModelViewSet):
    queryset = Movable.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MovableReadSerializer
        return MovableWriteSerializer

    def get_permissions(self):
        if self.request.method in ['HEAD', 'OPTIONS', 'POST']:
            return (permissions.AllowAny(), )
        return (permissions.IsAuthenticated(), )

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(account=account)
        serializer = self.get_serializer_class()(queryset, many=True, context={'request': request})
        return Response(serializer.data)

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
        #    instance.photo = self.request.FILES.get('file')

        serializer = self.get_serializer_class()(instance, data=request.data)

        if serializer.is_valid():
            if serializer.save(user=user):
                if 'photo' in serializer.validated_data: #delete this field from the response as it isn't serializable
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
                            'WHERE m.account_id = %s AND s.first_seen_at >= %s AND s.last_seen_at <= %s ' + \
                            'AND (%s OR s.place_id = ANY(%s)) AND s.last_seen_at IN (' + \
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

            # serializer = self.get_pagination_serializer(page)
            # page = self.paginate_queryset(queryset)
            serializer = self.get_serializer_class()(queryset, many=True, context={'request': request})
            return Response(serializer.data)
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
                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AutoSightingView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = json.loads(request.body.decode('utf-8'))

        company_id = data.get('company_id', None)
        account = None
        watcher_uid = data.get('watcher_uid', None)
        place = None
        user = None
        movable_uid = data.get('movable_uid', None)
        movable = None
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
                Place.objects.create(account=account, uid=watcher_uid)

        sightings = Sighting.objects.filter(movable=movable, place=place, user=user, is_current=True).\
                    order_by('-last_seen_at')
        if sightings:
            sighting = sightings[0]
            sighting.last_seen_at = None  # this forces the datetime update
            sighting.rssi = rssi
            sighting.battery = battery
            sighting.save()
            # Need to check for events for this sighting
        else:
            sighting = Sighting.objects.create(movable=movable, place=place, user=user, rssi=rssi, battery=battery)
            # Need to check for sightings that need closing and check for events on both the old and the new one

        if sighting:
            serialized = SightingReadSerializer(sighting, context={'request': request})
            return Response(serialized.data)
        else:
            return Response('Failed to create sighting.', status=status.HTTP_400_BAD_REQUEST)