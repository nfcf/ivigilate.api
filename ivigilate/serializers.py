from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers
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


class AuthUserSerializer(serializers.HyperlinkedModelSerializer):
    company_id = serializers.CharField(source='account.company_id', required=True)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = AuthUser
        fields = ('id', 'company_id', 'email', 'first_name', 'last_name', 'metadata', 'created_at', 'updated_at',
                  'password', 'confirm_password',)
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_company_id(self, value):
        try:
            Account.objects.get(company_id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')
        return value

    def create(self, validated_data):
        company_id = validated_data.get('account.company_id')
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


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = Place
        fields = ('id', 'account', 'uuid', 'reference_id', 'name',
                  'location', 'arrival_rssi', 'departure_rssi',
                  'metadata', 'created_at', 'updated_at', 'is_active')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        return Place.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.reference_id = validated_data.get('reference_id', instance.reference_id)
        instance.name = validated_data.get('name', instance.name)
        instance.location = validated_data.get('location', instance.location)
        instance.arrival_rssi = validated_data.get('arrival_rssi', instance.arrival_rssi)
        instance.departure_rssi = validated_data.get('departure_rssi', instance.departure_rssi)
        instance.metadata = validated_data.get('name', instance.metadata)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()

        return instance


class MovableSerializer(serializers.HyperlinkedModelSerializer):
    company_id = serializers.CharField(source='account.company_id', required=True)
    arrival_rssi = serializers.IntegerField(allow_null=True, default=-75)
    departure_rssi = serializers.IntegerField(allow_null=True, default=-90)

    class Meta:
        model = Movable
        fields = ('id', 'company_id', 'uuid', 'reference_id', 'photo',
                  'first_name', 'last_name', 'type', 'arrival_rssi', 'departure_rssi',
                  'metadata', 'reported_missing', 'created_at', 'updated_at', 'is_active')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_company_id(self, value):
        try:
            Account.objects.get(company_id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')
        return value

    def create(self, validated_data):
        company_id = validated_data.get('account.company_id')
        try:
            account = Account.objects.get(company_id=company_id)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')

        uuid = validated_data.get('uuid')
        type = validated_data.get('type')
        metadata = validated_data.get('metadata')

        return Movable.objects.create(account=account, uuid=uuid, type=type, metadata=metadata)

    def update(self, instance, validated_data):
        instance.reference_id = validated_data.get('reference_id', instance.reference_id)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.type = validated_data.get('type', instance.type)
        instance.arrival_rssi = validated_data.get('arrival_rssi', instance.arrival_rssi)
        instance.departure_rssi = validated_data.get('departure_rssi', instance.departure_rssi)
        instance.metadata = validated_data.get('name', instance.metadata)
        instance.reported_missing = validated_data.get('reported_missing', instance.reported_missing)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()

        return instance


class SightingSerializer(serializers.ModelSerializer):
    movable = MovableSerializer()

    class Meta:
        model = Sighting
        fields = ('id', 'movable', 'watcher_id', 'first_seen_at', 'last_seen_at',
                  'location', 'rssi', 'battery_level', 'metadata', 'confirmed',
                  'confirmed_by', 'confirmed_at', 'comment', 'commented_by', 'commented_at', 'is_active')
        read_only_fields = ('id', 'first_seen_at', 'last_seen_at', 'confirmed_at', 'commented_at')

    def create(self, validated_data):
        return Sighting.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.location = validated_data.get('location', instance.location)

        instance.rssi = validated_data.get('rssi', instance.rssi)
        instance.battery_level = validated_data.get('battery_lavel', instance.battery_lavel)
        instance.metadata = validated_data.get('name', instance.metadata)
        instance.confirmed = validated_data.get('confirmed', instance.confirmed)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()

        return instance