from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers
from ivigilate.models import *
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class LicenseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = License
        fields = ('reference_id', 'amount', 'currency', 'description', 'metadata', 'valid_from', 'valid_until')
        write_only_fields = 'reference_id'


class AccountSerializer(serializers.ModelSerializer):
    licenses = LicenseSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ('id', 'company_id', 'name', 'metadata', 'created_at', 'licenses')
        read_only_fields = 'created_at'

    def create(self, validated_data):
        return Account.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.company_id = validated_data.get('company_id', instance.company_id)
        instance.name = validated_data.get('name', instance.name)
        instance.metadata = validated_data.get('metadata', instance.metadata)
        instance.save()

        return instance


class AuthUserReadSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(source='account.company_id')
    token = serializers.CharField(source='get_token', read_only=True)
    license_about_to_expire = LicenseSerializer(source='account.get_license_about_to_expire', read_only=True)
    license_due_for_payment = LicenseSerializer(source='account.get_license_due_for_payment', read_only=True)

    class Meta:
        model = AuthUser
        fields = ('id', 'company_id', 'email', 'first_name', 'last_name',
                  'metadata', 'is_account_admin', 'is_active', 'token',
                  'created_at', 'updated_at', 'license_about_to_expire', 'license_due_for_payment')


class AuthUserWriteSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(source='account.company_id', required=True)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = AuthUser
        fields = ('id', 'company_id', 'email', 'first_name', 'last_name',
                  'metadata', 'is_account_admin', 'is_active', 'password', 'confirm_password')

    def validate_company_id(self, value):
        try:
            Account.objects.get(company_id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')
        return value

    def create(self, validated_data):
        return AuthUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.metadata = validated_data.get('metadata', instance.metadata)
        instance.is_account_admin = validated_data.get('is_account_admin', instance.is_account_admin)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()

        password1 = validated_data.get('password', None)
        password2 = validated_data.get('confirm_password', None)

        if password1 and password2 and password1 == password2:
            instance.set_password(password1)
            instance.save()

        return instance


class DetectorBeaconHistorySerializer(gis_serializers.GeoModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Detector
        geo_field = 'location'
        fields = ('id', 'uid', 'reference_id', 'type', 'type_display', 'is_active')


class DetectorReadSerializer(gis_serializers.GeoModelSerializer):
    account = serializers.HyperlinkedIdentityField(view_name='account-detail')
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Detector
        geo_field = 'location'
        fields = ('id', 'account', 'uid', 'reference_id', 'type', 'type_display', 'photo', 'name',
                  'location', 'arrival_rssi', 'departure_rssi',
                  'created_at', 'updated_at', 'updated_by', 'is_active')


class DetectorWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detector
        geo_field = 'location'
        fields = ('reference_id', 'type', 'photo', 'name', 'location',
                  'arrival_rssi', 'departure_rssi', 'metadata', 'is_active')

    def create(self, validated_data):
        detector = Detector.objects.create(**validated_data)
        return detector

    def update(self, instance, validated_data):
        instance.reference_id = validated_data.get('reference_id', instance.reference_id)
        instance.type = validated_data.get('type', instance.type)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.name = validated_data.get('name', instance.name)
        instance.location = validated_data.get('location', instance.location)
        instance.arrival_rssi = validated_data.get('arrival_rssi', instance.arrival_rssi)
        instance.departure_rssi = validated_data.get('departure_rssi', instance.departure_rssi)
        instance.metadata = validated_data.get('metadata', instance.metadata)
        instance.updated_by = validated_data.get('user')
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class SimpleEventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'reference_id', 'name')


class BeaconDetectorHistorySerializer(gis_serializers.GeoModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Beacon
        geo_field = 'location'
        fields = ('id', 'uid', 'reference_id', 'type', 'type_display', 'is_active')


class BeaconReadSerializer(serializers.HyperlinkedModelSerializer):
    unauthorized_events = SimpleEventSerializer(many=True, read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Beacon
        geo_field = 'location'
        fields = ('id', 'account', 'uid', 'reference_id', 'type', 'type_display',
                  'name', 'photo', 'location', 'reported_missing', 'unauthorized_events',
                  'metadata', 'created_at', 'updated_at', 'updated_by', 'is_active')


class BeaconWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beacon
        geo_field = 'location'
        fields = ('reference_id', 'type', 'name', 'photo', 'location', 'reported_missing',
                  'metadata', 'created_at', 'updated_at', 'is_active')

    def validate_company_id(self, value):
        try:
            Account.objects.get(company_id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')
        return value

    def create(self, validated_data):
        beacon = Beacon.objects.create(**validated_data)
        return beacon

    def update(self, instance, validated_data):
        instance.reference_id = validated_data.get('reference_id', instance.reference_id)
        instance.type = validated_data.get('type', instance.type)
        instance.name = validated_data.get('name', instance.name)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.metadata = validated_data.get('metadata', instance.metadata)
        instance.location = validated_data.get('location', instance.location)
        instance.reported_missing = validated_data.get('reported_missing', instance.reported_missing)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.updated_by = validated_data.get('user')
        instance.save()

        return instance


class SightingBeaconHistorySerializer(gis_serializers.GeoModelSerializer):
    beacon = serializers.CharField(source='get_beacon_uid', read_only=True)
    detector = DetectorBeaconHistorySerializer()
    duration_in_seconds = serializers.IntegerField(source='get_duration', read_only=True)

    class Meta:
        model = Sighting
        geo_field = 'location'
        fields = ('id', 'beacon', 'detector', 'first_seen_at', 'last_seen_at', 'duration_in_seconds',
                  'location', 'beacon_battery', 'metadata', 'is_active')


class SightingDetectorHistorySerializer(gis_serializers.GeoModelSerializer):
    detector = serializers.CharField(source='get_detector_uid', read_only=True)
    beacon = BeaconDetectorHistorySerializer()
    duration_in_seconds = serializers.IntegerField(source='get_duration', read_only=True)

    class Meta:
        model = Sighting
        geo_field = 'location'
        fields = ('id', 'beacon', 'detector', 'first_seen_at', 'last_seen_at', 'duration_in_seconds',
                  'location', 'beacon_battery', 'metadata', 'is_active')


#version 2 Sighting beacon and detector history serializer

class SightingBeaconOrDetectorHistorySerializerV2(gis_serializers.GeoModelSerializer):
    beacon = BeaconDetectorHistorySerializer()
    detector = DetectorBeaconHistorySerializer()
    duration_in_seconds = serializers.IntegerField(source='get_duration', read_only=True)

    class Meta:
        model = Sighting
        geo_field = 'location'
        fields = ('id', 'beacon', 'detector', 'first_seen_at', 'last_seen_at', 'duration_in_seconds',
                  'location', 'beacon_battery', 'metadata', 'is_active')



class SightingReadSerializer(gis_serializers.GeoModelSerializer):
    beacon = BeaconReadSerializer()
    detector = DetectorReadSerializer()

    class Meta:
        model = Sighting
        geo_field = 'location'
        fields = ('id', 'detector', 'detector_battery', 'beacon', 'beacon_battery', 'first_seen_at', 'last_seen_at',
                  'location', 'rssi', 'metadata', 'confirmed',
                  'confirmed_by', 'confirmed_at', 'comment', 'commented_by', 'commented_at', 'is_active')


class SightingWriteSerializer(gis_serializers.GeoModelSerializer):
    first_seen_at = serializers.DateTimeField(allow_null=True, required=False)
    last_seen_at = serializers.DateTimeField(allow_null=True, required=False)
    location = serializers.CharField(allow_null=True, required=False)
    detector_battery = serializers.IntegerField(allow_null=True, required=False)
    beacon_battery = serializers.IntegerField(allow_null=True, required=False)
    rssi = serializers.IntegerField(allow_null=True, required=False)
    confirmed = serializers.BooleanField(default=False)

    class Meta:
        model = Sighting
        geo_field = 'location'
        fields = ('id', 'detector', 'detector_battery', 'beacon', 'beacon_battery', 'first_seen_at', 'last_seen_at',
                  'location', 'rssi', 'metadata', 'confirmed', 'comment')

    def create(self, validated_data):
        validated_data['confirmed_by'] = validated_data.get('user') if validated_data.get('confirmed') else None
        validated_data['commented_by'] = validated_data.get('user') if validated_data.get('comment') else None

        existing_sighting = Sighting.objects.filter(beacon=validated_data.get('beacon'),
                                                    detector=validated_data.get('detector'),
                                                    first_seen_at__lte=validated_data.get('first_seen_at'),
                                                    last_seen_at__gt=validated_data.get('first_seen_at'),
                                                    last_seen_at__lte=validated_data.get('last_seen_at')).order_by('-id')[:1]

        if (existing_sighting is not None and len(existing_sighting) > 0):
            sighting = existing_sighting[0]
            sighting.last_seen_at = validated_data.get('last_seen_at')
            sighting.comment = validated_data.get('comment')
            sighting.commented_by = validated_data.get('commented_by')
            sighting.save()
        else:
            if not validated_data.get('location') and validated_data.get('detector'):
                validated_data['location'] = validated_data.get('detector').location

            if not validated_data.get('comment'):
                raise serializers.ValidationError('Comment field cannot be empty.')

            del validated_data['user']
            sighting = Sighting.objects.create(**validated_data)

        return sighting

    def update(self, instance, validated_data):
        instance.location = validated_data.get('location', instance.location)

        instance.rssi = validated_data.get('rssi', instance.rssi)
        instance.detector_battery = validated_data.get('detector_battery', instance.detector_battery)
        instance.beacon_battery = validated_data.get('beacon_battery', instance.beacon_battery)
        instance.metadata = validated_data.get('metadata', instance.metadata)
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
        instance.save()

        return instance


class EventBeaconSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Beacon
        fields = ('id', 'reference_id', 'name')


class EventDetectorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Detector
        fields = ('id', 'reference_id', 'name')


class EventReadSerializer(serializers.HyperlinkedModelSerializer):
    detectors = EventDetectorSerializer(many=True, read_only=True)
    unauthorized_beacons = EventBeaconSerializer(many=True, read_only=True)
    authorized_beacons = EventBeaconSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'account', 'reference_id', 'name', 'detectors', 'unauthorized_beacons', 'authorized_beacons',
                  'schedule_days_of_week', 'schedule_start_time', 'schedule_end_time', 'schedule_timezone_offset',
                  'metadata', 'created_at', 'updated_at', 'updated_by', 'is_active')


class EventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'reference_id', 'name',
                  'schedule_days_of_week', 'schedule_start_time', 'schedule_end_time', 'schedule_timezone_offset',
                  'metadata', 'is_active')

    def update(self, instance, validated_data):
        instance.reference_id = validated_data.get('reference_id', instance.reference_id)
        instance.name = validated_data.get('name', instance.name)
        instance.schedule_days_of_week = validated_data.get('schedule_days_of_week', instance.schedule_days_of_week)
        instance.schedule_start_time = validated_data.get('schedule_start_time', instance.schedule_start_time)
        instance.schedule_end_time = validated_data.get('schedule_end_time', instance.schedule_end_time)
        instance.schedule_timezone_offset = validated_data.get('schedule_timezone_offset', instance.schedule_timezone_offset)

        instance.metadata = validated_data.get('metadata', instance.metadata)
        instance.updated_by = validated_data.get('updated_by')
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class LimitReadSerializer(serializers.ModelSerializer):
    events = EventReadSerializer(many=True, read_only=True)
    beacons = EventBeaconSerializer(many=True, read_only=True)

    class Meta:
        model = Limit
        fields = ('id', 'account', 'reference_id', 'name', 'events', 'beacons', 'start_date',
                  'metadata', 'created_at', 'updated_at', 'updated_by', 'is_active')


class LimitWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Limit
        fields = ('id', 'reference_id', 'name', 'start_date', 'metadata', 'is_active')

    def update(self, instance, validated_data):
        instance.reference_id = validated_data.get('reference_id', instance.reference_id)
        instance.name = validated_data.get('name', instance.name)
        instance.start_date = validated_data.get('start_date', instance.start_date)

        instance.metadata = validated_data.get('metadata', instance.metadata)
        instance.updated_by = validated_data.get('updated_by')
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'metadata', 'created_at', 'is_active')
        read_only_fields = 'created_at'

    def create(self, validated_data):
        return Account.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.updated_by = validated_data.get('updated_by')
        instance.save()

        return instance