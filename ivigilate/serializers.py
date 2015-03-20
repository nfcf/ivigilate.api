from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers
from ivigilate.models import *

class LicenseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = License
        fields = ('type', 'max_movables', 'max_users', 'metadata', 'valid_from', 'valid_until')
        read_only_fields = ()
        write_only_fields = ('metadata',)

    def create(selfself, validated_data):
        return License.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.type = validated_data.get('type', instance.type)
        instance.max_movables = validated_data.get('max_movables', instance.max_movables)
        instance.max_users = validated_data.get('max_users', instance.max_users)
        instance.metadata = validated_data.get('metadata', instance.metadata)
        instance.valid_from = validated_data.get('valid_from', instance.valid_from)
        instance.valid_until = validated_data.get('valid_until', instance.valid_until)
        instance.save()

        return instance


class AccountSerializer(serializers.ModelSerializer):
    licenses = LicenseSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ('id', 'company_id', 'name', 'metadata', 'created_at', 'licenses')
        read_only_fields = ('created_at')

    def create(selfself, validated_data):
        return Account.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.company_id = validated_data.get('company_id', instance.company_id)
        instance.name = validated_data.get('name', instance.name)
        instance.metadata = validated_data.get('metadata', instance.metadata)
        instance.save()

        return instance

class AuthUserReadSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(source='account.company_id', required=True)
    class Meta:
        model = AuthUser
        fields = ('id', 'company_id', 'email', 'first_name', 'last_name', 'metadata', 'created_at', 'updated_at',)

class AuthUserWriteSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(source='account.company_id', required=True)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = AuthUser
        fields = ('id', 'company_id', 'email', 'first_name', 'last_name', 'metadata',
                  'password', 'confirm_password',)

    def validate_company_id(self, value):
        try:
            Account.objects.get(company_id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')
        return value

    def create(self, validated_data):
        company_id = validated_data.get('account').get('company_id')
        email = validated_data.get('email')
        password = validated_data.get('password')
        try:
            account = Account.objects.get(company_id=company_id)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')

        return AuthUser.objects.create_user(account=account, email=email, password=password)

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.metadata = validated_data.get('metadata', instance.metadata)

        instance.save()

        password1 = validated_data.get('password', None)
        password2 = validated_data.get('confirm_password', None)

        if password1 and password2 and password1 == password2:
            instance.set_password(password1)
            instance.save()

        update_session_auth_hash(self.context.get('request'), instance)

        return instance


class PlaceReadSerializer(gis_serializers.GeoModelSerializer):
    class Meta:
        model = Place
        geo_field = 'location'
        fields = ('id', 'account', 'uid', 'reference_id', 'name',
                  'location', 'arrival_rssi', 'departure_rssi',
                  'metadata', 'created_at', 'updated_at', 'updated_by', 'is_active')


class PlaceWriteSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(source='account.company_id', required=False)

    class Meta:
        model = Place
        geo_field = 'location'
        fields = ('id', 'company_id', 'uid', 'reference_id', 'name',
                  'location', 'arrival_rssi', 'departure_rssi',
                  'metadata', 'is_active')

    def create(self, validated_data):
        company_id = validated_data.get('account').get('company_id')
        try:
            account = Account.objects.get(company_id=company_id)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')

        uid = validated_data.get('uid')
        metadata = validated_data.get('metadata')

        return Place.objects.create(account=account, uid=uid, metadata=metadata)

    def update(self, instance, validated_data):
        instance.reference_id = validated_data.get('reference_id', instance.reference_id)
        instance.name = validated_data.get('name', instance.name)
        instance.location = validated_data.get('location', instance.location)
        instance.arrival_rssi = validated_data.get('arrival_rssi', instance.arrival_rssi)
        instance.departure_rssi = validated_data.get('departure_rssi', instance.departure_rssi)
        instance.metadata = validated_data.get('name', instance.metadata)
        instance.updated_by = validated_data.get('user')
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class MovableReadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Movable
        fields = ('id', 'account', 'uid', 'reference_id', 'photo',
                  'name', 'arrival_rssi', 'departure_rssi', 'metadata',
                  'reported_missing', 'created_at', 'updated_at', 'updated_by', 'is_active')


class MovableWriteSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(source='account.company_id', required=True)
    arrival_rssi = serializers.IntegerField(default=-75)
    departure_rssi = serializers.IntegerField(default=-90)

    class Meta:
        model = Movable
        fields = ('id', 'company_id', 'uid', 'reference_id', 'photo',
                  'name', 'arrival_rssi', 'departure_rssi', 'metadata',
                  'reported_missing', 'created_at', 'updated_at', 'updated_by', 'is_active')

    def validate_company_id(self, value):
        try:
            Account.objects.get(company_id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')
        return value

    def create(self, validated_data):
        company_id = validated_data.get('account').get('company_id')
        try:
            account = Account.objects.get(company_id=company_id)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')

        uid = validated_data.get('uid')
        metadata = validated_data.get('metadata')

        return Movable.objects.create(account=account, uid=uid, metadata=metadata)

    def update(self, instance, validated_data):
        instance.reference_id = validated_data.get('reference_id', instance.reference_id)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.name = validated_data.get('name', instance.name)
        instance.arrival_rssi = validated_data.get('arrival_rssi', instance.arrival_rssi)
        instance.departure_rssi = validated_data.get('departure_rssi', instance.departure_rssi)
        instance.metadata = validated_data.get('name', instance.metadata)
        instance.reported_missing = validated_data.get('reported_missing', instance.reported_missing)
        instance.updated_by = validated_data.get('user')
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class SightingReadSerializer(serializers.ModelSerializer):
    movable = MovableReadSerializer()
    location_name = serializers.CharField(source='get_location_name', read_only=True)

    class Meta:
        model = Sighting
        fields = ('id', 'movable', 'first_seen_at', 'last_seen_at',
                  'location', 'location_name', 'rssi', 'battery', 'metadata', 'confirmed',
                  'confirmed_by', 'confirmed_at', 'comment', 'commented_by', 'commented_at', 'is_current')

class SightingWriteSerializer(serializers.ModelSerializer):
    movable_uid = serializers.CharField(source='movable.uid', required=True)
    location = serializers.CharField(allow_blank=True, required=False)
    battery = serializers.IntegerField(allow_null=True, required=False)
    rssi = serializers.IntegerField(allow_null=True, required=False)
    confirmed = serializers.BooleanField(default=False)
    is_current = serializers.BooleanField(default=True)

    class Meta:
        model = Sighting
        fields = ('id', 'movable_uid', 'watcher_uid',
                  'location', 'rssi', 'battery', 'metadata',
                  'confirmed', 'comment', 'is_current')


    def validate_movable_uid(self, value):
        try:
            Movable.objects.get(uid=value)
        except Movable.DoesNotExist:
            raise serializers.ValidationError('Invalid Movable UID.')
        return value

    def validate_watcher_uid(self, value):
        if '@' in value:
            try:
                AuthUser.objects.get(email=value)
            except AuthUser.DoesNotExist:
                raise serializers.ValidationError('Invalid Watcher UID.')
        else:
            try:
                Place.objects.get(uid=value)
            except Place.DoesNotExist:
                raise serializers.ValidationError('Invalid Watcher UID.')
        return value

    def create(self, validated_data):
        movable_uid = validated_data.get('movable').get('uid')
        try:
            movable = Movable.objects.get(uid=movable_uid)
        except Movable.DoesNotExist:
            raise serializers.ValidationError('Invalid Movable UID.')
        watcher_uid = validated_data.get('watcher_uid')
        location = validated_data.get('location')
        rssi = validated_data.get('rssi')
        battery = validated_data.get('battery')
        metadata = validated_data.get('metadata') if validated_data.get('metadata') else ''
        confirmed = validated_data.get('confirmed')
        confirmed_by = validated_data.get('user') if validated_data.get('confirmed') else None
        comment = validated_data.get('comment')
        commented_by = validated_data.get('user') if validated_data.get('comment') else None
        is_current = validated_data.get('is_current')

        return Sighting.objects.create(movable=movable, watcher_uid=watcher_uid, location=location,
                                       rssi=rssi, battery=battery, metadata=metadata,
                                       confirmed=confirmed, confirmed_by=confirmed_by, comment=comment,
                                       commented_by=commented_by, is_current=is_current)

    def update(self, instance, validated_data):
        instance.location = validated_data.get('location', instance.location)

        instance.rssi = validated_data.get('rssi', instance.rssi)
        instance.battery = validated_data.get('battery', instance.battery)
        instance.metadata = validated_data.get('name', instance.metadata)
        instance.confirmed = validated_data.get('confirmed', instance.confirmed)
        confirmed_by_user_email = validated_data.get('confirmed_by_user_email')
        try:
            if confirmed_by_user_email:
                instance.confirmed_by = AuthUser.objects.get(email=confirmed_by_user_email)
        except AuthUser.DoesNotExist:
            raise serializers.ValidationError('Invalid Confirmed by User.')
        commented_by_user_email = validated_data.get('commented_by_user_email')
        try:
            if commented_by_user_email:
                instance.commented_by = AuthUser.objects.get(email=commented_by_user_email)
        except AuthUser.DoesNotExist:
            raise serializers.ValidationError('Invalid Commented by User.')

        instance.comment = validated_data.get('comment', instance.comment)
        instance.is_current = validated_data.get('is_current', instance.is_current)
        instance.save()

        return instance