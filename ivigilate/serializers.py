from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers
from ivigilate.models import *
from ivigilate.utils import get_file_extension, check_for_events
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)


class LicenseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = License
        fields = ('type', 'max_movables', 'max_users', 'metadata', 'valid_from', 'valid_until')
        read_only_fields = ()
        write_only_fields = ('metadata',)

    def create(self, validated_data):
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
    account = serializers.HyperlinkedIdentityField(view_name='account-detail')

    class Meta:
        model = Place
        geo_field = 'location'
        fields = ('id', 'account', 'uid', 'reference_id', 'name',
                  'location', 'arrival_rssi', 'departure_rssi',
                  'created_at', 'updated_at', 'updated_by', 'is_active')


class PlaceWriteSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(source='account.company_id', required=False)

    class Meta:
        model = Place
        geo_field = 'location'
        fields = ('id', 'company_id', 'uid', 'reference_id', 'name',
                  'location', 'arrival_rssi', 'departure_rssi',
                  'metadata', 'is_active')

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


class MovableEventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'reference_id', 'name')


class MovableReadSerializer(serializers.HyperlinkedModelSerializer):
    events = MovableEventSerializer(many=True, read_only=True)

    class Meta:
        model = Movable
        fields = ('id', 'account', 'uid', 'reference_id', 'name',
                  'photo', 'reported_missing', 'events',
                  'metadata', 'created_at', 'updated_at', 'updated_by', 'is_active')


class MovableWriteSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(source='account.company_id', required=False)

    class Meta:
        model = Movable
        fields = ('id', 'company_id', 'uid', 'reference_id', 'name',
                  'photo', 'reported_missing',
                  'metadata', 'created_at', 'updated_at', 'is_active')

    def validate_company_id(self, value):
        try:
            Account.objects.get(company_id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')
        return value

    def update(self, instance, validated_data):
        instance.reference_id = validated_data.get('reference_id', instance.reference_id)
        instance.name = validated_data.get('name', instance.name)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.metadata = validated_data.get('metadata', instance.metadata)
        instance.reported_missing = validated_data.get('reported_missing', instance.reported_missing)
        instance.updated_by = validated_data.get('user')
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class SightingReadSerializer(gis_serializers.GeoModelSerializer):
    movable = MovableReadSerializer()
    place = PlaceReadSerializer()
    user = serializers.HyperlinkedIdentityField(view_name='authuser-detail')
    location_name = serializers.CharField(source='get_location_name', read_only=True)

    class Meta:
        model = Sighting
        geo_field = 'location'
        fields = ('id', 'movable', 'place', 'user', 'first_seen_at', 'last_seen_at',
                  'location', 'location_name', 'rssi', 'battery', 'metadata', 'confirmed',
                  'confirmed_by', 'confirmed_at', 'comment', 'commented_by', 'commented_at', 'is_current')


class SightingWriteSerializer(gis_serializers.GeoModelSerializer):
    first_seen_at = serializers.DateTimeField(allow_null=True, required=False)
    last_seen_at = serializers.DateTimeField(allow_null=True, required=False)
    location = serializers.CharField(allow_null=True, required=False)
    battery = serializers.IntegerField(allow_null=True, required=False)
    rssi = serializers.IntegerField(allow_null=True, required=False)
    confirmed = serializers.BooleanField(default=False)

    class Meta:
        model = Sighting
        geo_field = 'location'
        fields = ('id', 'movable', 'place', 'first_seen_at', 'last_seen_at',
                  'location', 'rssi', 'battery', 'metadata', 'confirmed', 'comment')

    def create(self, validated_data):
        validated_data['confirmed_by'] = validated_data.get('user') if validated_data.get('confirmed') else None
        validated_data['commented_by'] = validated_data.get('user') if validated_data.get('comment') else None

        if not validated_data.get('location') and validated_data.get('place'):
            validated_data['location'] = validated_data.get('place').location

        if not validated_data.get('comment'):
            raise serializers.ValidationError('Comment field cannot be empty.')

        sighting = Sighting.objects.create(**validated_data)
        check_for_events(sighting)
        return sighting

    def update(self, instance, validated_data):
        instance.location = validated_data.get('location', instance.location)

        instance.rssi = validated_data.get('rssi', instance.rssi)
        instance.battery = validated_data.get('battery', instance.battery)
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


class EventMovableSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Movable
        fields = ('id', 'reference_id', 'name')


class EventPlaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Place
        fields = ('id', 'reference_id', 'name')


class EventEventOccurrenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventOccurrence
        fields = ('id', 'event')


class EventReadSerializer(serializers.HyperlinkedModelSerializer):
    movables = EventMovableSerializer(many=True, read_only=True)
    places = EventPlaceSerializer(many=True, read_only=True)
    sighting_previous_event_occurrence = EventEventOccurrenceSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'account', 'reference_id', 'name', 'movables', 'places',
                  'schedule_days_of_week', 'schedule_start_time', 'schedule_end_time',
                  'sighting_is_current', 'sighting_duration_in_seconds', 'sighting_has_battery_below',
                  'sighting_has_comment', 'sighting_has_been_confirmed', 'sighting_previous_event_occurrence',
                  'metadata', 'created_at', 'updated_at', 'updated_by', 'is_active')


class EventWriteSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(source='account.company_id', required=False)
    sighting_previous_event_occurrence = serializers.IntegerField(required=False)

    class Meta:
        model = Event
        fields = ('id', 'company_id', 'reference_id', 'name',
                  'schedule_days_of_week', 'schedule_start_time', 'schedule_end_time',
                  'sighting_is_current', 'sighting_duration_in_seconds', 'sighting_has_battery_below',
                  'sighting_has_comment', 'sighting_has_been_confirmed', 'sighting_previous_event_occurrence',
                  'metadata', 'is_active')

    def create(self, validated_data):
        company_id = validated_data.get('account').get('company_id')
        try:
            account = Account.objects.get(company_id=company_id)
        except Account.DoesNotExist:
            raise serializers.ValidationError('Invalid Company ID.')

        validated_data['account'] = account
        return Event.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.reference_id = validated_data.get('reference_id', instance.reference_id)
        instance.name = validated_data.get('name', instance.name)
        instance.schedule_days_of_week = validated_data.get('schedule_days_of_week', instance.schedule_days_of_week)
        instance.schedule_start_time = validated_data.get('schedule_start_time', instance.schedule_start_time)
        instance.schedule_end_time = validated_data.get('schedule_end_time', instance.schedule_end_time)

        instance.sighting_is_current = validated_data.get('sighting_is_current', instance.sighting_is_current)
        instance.sighting_duration_in_seconds = validated_data.get('sighting_duration_in_seconds', instance.sighting_duration_in_seconds)
        instance.sighting_has_battery_below = validated_data.get('sighting_has_battery_below', instance.sighting_has_battery_below)
        instance.sighting_has_comment = validated_data.get('sighting_has_comment', instance.sighting_has_comment)
        instance.sighting_has_been_confirmed = validated_data.get('sighting_has_been_confirmed', instance.sighting_has_been_confirmed)
        # instance.sighting_previous_event_occurrence = validated_data.get('sighting_previous_event_occurrence', instance.sighting_previous_event_occurrence)

        instance.metadata = validated_data.get('name', instance.metadata)
        instance.updated_by = validated_data.get('user')
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance