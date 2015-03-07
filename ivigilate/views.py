from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from ivigilate.serializers import *
from ivigilate.permissions import IsAccountOwner
from rest_framework import permissions, viewsets, status, views
from django.shortcuts import get_object_or_404

import json

class IndexView(TemplateView):
    template_name = 'index.html'

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)


class AccountViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(),)

    def list(self, request):
        if request.user and request.user.is_staff:
            #return only the list of active accounts
            queryset = self.queryset.filter(licenses__valid_until__gt=datetime.now(timezone.utc)).distinct()

            page = self.paginate_queryset(queryset)
            serializer = self.get_pagination_serializer(page)
            return Response(serializer.data)
        else:
            return Response({
            'status': 'Bad request',
            'message': 'You do not have permissions to access this list.'
            }, status=status.HTTP_400_BAD_REQUEST)

    #def create(self, request):
    #    pass

    def retrieve(self, request, id=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        if account.id == int(id):
            try:
                queryset = self.queryset.get(id=id)
            except Account.DoesNotExist:
                return Response({
                'status': 'Bad request',
                'message': 'Account does not exist.'
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(queryset, many=False, context={'request': request})
            return Response(serializer.data)
        else:
            return Response({
                'status': 'Bad request',
                'message': 'You do not have permissions to access this account information.'
                }, status=status.HTTP_400_BAD_REQUEST)

    #def update(self, request, pk=None):
    #    pass

    #def partial_update(self, request, pk=None):
    #    pass

    #def destroy(self, request, pk=None):
    #    pass


class AuthUserViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)

        if self.request.method == 'POST':
            return (permissions.AllowAny(),)

        return (permissions.IsAuthenticated(), IsAccountOwner(),)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        errorMessage = None

        password = request.data.get('password', None)
        if password is None:
            errorMessage = "Password cannot be left empty."
        elif serializer.is_valid():
            if serializer.save():
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        if errorMessage is None:
            errorMessage = serializer.errors

        return Response({
            'status': 'Bad request',
            'message': errorMessage
            }, status=status.HTTP_400_BAD_REQUEST)


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
                serialized = AuthUserSerializer(user, context={'request': request})
                return Response(serialized.data)
            else:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'This user has been disabled.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Email/password combination invalid.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class PlaceViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)

        if self.request.method == 'POST':
            return (permissions.AllowAny(),)

        return (permissions.IsAuthenticated(), )

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            if serializer.save():
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'Bad request',
            'message': 'Place could not be created with received data: ' + serializer.error_messages
            }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(account=account)
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, id=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=id,account=account)
        except Place.DoesNotExist:
            return Response({
            'status': 'Bad request',
            'message': 'Place does not exist or is not associated with the current logged on account.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(queryset, many=False, context={'request': request})
        return Response(serializer.data)


class MovableViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Movable.objects.all()
    serializer_class = MovableSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return (permissions.AllowAny(),)

        return (permissions.IsAuthenticated(), )

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            if serializer.save():
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'Bad request',
            'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(account=account)
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, id=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=id,account=account)
        except Movable.DoesNotExist:
            return Response({
            'status': 'Bad request',
            'message': 'Movable does not exist or is not associated with the current logged on account.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(queryset, many=False, context={'request': request})
        return Response(serializer.data)


class SightingViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = Sighting.objects.all()
    serializer_class = SightingSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)

        if self.request.method == 'POST':
            return (permissions.AllowAny(),)

        return (permissions.IsAuthenticated(), )

    def list(self, request):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        queryset = self.queryset.filter(movable__account=account).order_by('-last_seen_at')
        page = self.paginate_queryset(queryset)
        serializer = self.get_pagination_serializer(page)
        return Response(serializer.data)

    def retrieve(self, request, id=None):
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=id,movable__account=account)
        except Sighting.DoesNotExist:
            return Response({
            'status': 'Bad request',
            'message': 'Sighting does not exist or is not associated with the current logged on account.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    def update(self, request, id=None):
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        account = request.user.account if not isinstance(request.user, AnonymousUser) else None
        try:
            queryset = self.queryset.get(id=id,movable__account=account)
        except Sighting.DoesNotExist:
            return Response({
            'status': 'Bad request',
            'message': 'Sighting does not exist or is not associated with the current logged on account.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(queryset, data=request.data)
        if serializer.is_valid():
            if serializer.save():
                return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)

        return Response({
            'status': 'Bad request',
            'message': 'Sighting could not be updated with received data: ' + serializer.error_messages
            }, status=status.HTTP_400_BAD_REQUEST)