from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import datetime, timezone
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from geoposition.fields import GeopositionField


class Account(models.Model):
    company_id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=64)
    metadata = models.TextField(blank=True)
    created_at = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now

        super(Account, self).save(*args, **kwargs)

    def __str__(self):
        return '%s - %s' % (self.company_id, self.name)

#class Geofence(models.Model):
    #account_id = models.ForeignKey(Account)
    #geometry = GeopositionField()
    #radius_in_meters = models.DecimalField()
    #objects = models.GeoManager()

class License(models.Model):
    TYPE = (
        ('SAM', 'School Attendance Management'),
        ('EAM', 'Event Attendance Management'),
        ('SAC', 'Simple Attendance Control'),
        ('AC', 'Absence Control'),
        ('LF', 'Lost & Found'),
    )
    account = models.ForeignKey(Account)
    type = models.CharField(max_length=3, choices=TYPE)
    max_movables = models.IntegerField()
    max_users = models.IntegerField()
    metadata = models.TextField(blank=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)

class AuthUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, account, email, password, is_staff, is_superuser, **extra_fields):
        now = datetime.now(timezone.utc)

        email = self.normalize_email(email)
        user = self.model(account=account, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          created_at=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, account, email, password, **extra_fields):
        if not email:
            raise ValueError('The email address must be set')
        return self._create_user(account, email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The email address must be set')
        return self._create_user(None, email, password, True, True, **extra_fields)

class AuthUser(AbstractBaseUser, PermissionsMixin):
    account = models.ForeignKey(Account, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True,
        help_text=_('Required.'),
        error_messages={
            'unique': _("The given email address has already been registered."),
        })
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    metadata = models.TextField(blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    created_at = models.DateTimeField(_('created at'), editable=False)
    updated_at = models.DateTimeField(_('updated at'), editable=False)

    objects = AuthUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('settings')

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(AuthUser, self).save(*args, **kwargs)


class Event(models.Model):
    account = models.ForeignKey(Account)
    reference_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    metadata = models.TextField(blank=True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(Event, self).save(*args, **kwargs)

class Movable(models.Model):
    TYPE = (
        ('B', 'Beacon'),
        ('W', 'Watcher'),
        ('BW', 'Beacon & Watcher'),
    )

    account = models.ForeignKey(Account)
    uuid = models.CharField(max_length=36, unique=True)
    reference_id = models.CharField(max_length=64)
    photo = models.ImageField(upload_to='photos')
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    type = models.CharField(max_length=2, choices=TYPE)
    arrival_rssi = models.IntegerField(default=-75)
    departure_rssi = models.IntegerField(default=-90)
    metadata = models.TextField(blank=True)
    reported_missing = models.BooleanField(default=False)
    event_limits = models.ManyToManyField(Event, through='EventLimit', related_name='+')
    event_occurrences = models.ManyToManyField(Event, through='EventOccurrence', related_name='+')
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(Movable, self).save(*args, **kwargs)

class Place(models.Model):
    account = models.ForeignKey(Account)
    uuid = models.CharField(max_length=36, unique=True)
    reference_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    location = GeopositionField()
    arrival_rssi = models.IntegerField(default=-75)
    departure_rssi = models.IntegerField(default=-90)
    metadata = models.TextField(blank=True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    is_active = models.BooleanField(default=True)
    #objects = models.GeoManager()

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(Place, self).save(*args, **kwargs)

class Sighting(models.Model):
    movable = models.ForeignKey(Movable)
    watcher_id = models.CharField(max_length=32, db_index=True)
    first_seen_at = models.DateTimeField(editable=False)
    last_seen_at = models.DateTimeField(editable=False)
    location = GeopositionField()
    rssi = models.IntegerField()
    battery_level = models.IntegerField()
    metadata = models.TextField(blank=True)
    confirmed = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    confirmed_at = models.DateTimeField(null=True)
    comment = models.TextField()
    commented_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    commented_at = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    #objects = models.GeoManager()

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.first_seen_at = now
            self.last_seen_at = now
        else:
            self.last_seen_at = now
        super(Sighting, self).save(*args, **kwargs)

class Schedule(models.Model):
    account = models.ForeignKey(Account)
    group_id = models.CharField(max_length=64)
    reference_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    metadata = models.TextField(blank=True)
    places = models.ManyToManyField(Place)
    movables = models.ManyToManyField(Movable)
    events = models.ManyToManyField(Event)
    sightings = models.ManyToManyField(Sighting)

class EventTrigger(models.Model):
    event = models.ForeignKey(Event)
    movable = models.ForeignKey(Movable, null=True)
    #depends_on = models.ForeignKey(EventTrigger)
    is_occurring_after_X_seconds_since_last = models.IntegerField(default=0)
    is_going_on_for_longer_than_X_seconds = models.IntegerField(default=0)
    is_closed = models.BooleanField(default=False)
    has_battery_level_below = models.IntegerField(default=0)
    has_comment = models.BooleanField(default=False)
    occurred_in_at_least_X_places = models.IntegerField(default=0) #for guard tours

class EventOccurrence(models.Model):
    event = models.ForeignKey(Event)
    movable = models.ForeignKey(Movable)
    places = models.ManyToManyField(Place) #for guard tours
    duration = models.TimeField()
    occurred_at = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.occurred_at = now

        super(EventOccurrence, self).save(*args, **kwargs)

class EventLimit(models.Model):
    event = models.ForeignKey(Event)
    movable = models.ForeignKey(Movable)
    occurrence_date_limit = models.DateTimeField()
    occurrence_count_limit = models.IntegerField()
    occurrence_count = models.IntegerField(default=0) #not normalized but to make showing this on the UI easier
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(EventLimit, self).save(*args, **kwargs)

class EventAction(models.Model):
    TYPE = (
        ('T', 'Trigger'),
        ('L', 'Limit'),
    )

    event = models.ForeignKey(Event)
    type = models.CharField(max_length=1, choices=TYPE)
    #email
    #SMS
    #REST call
    metadata = models.TextField(blank=True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(EventAction, self).save(*args, **kwargs)
