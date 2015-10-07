from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import datetime, timezone, timedelta
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.db.models import Lookup


class BitwiseAnd(Lookup):
    lookup_name = 'bwand'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s & %s > 0' % (lhs, rhs), params

models.PositiveSmallIntegerField.register_lookup(BitwiseAnd)


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

    def get_license_in_force(self):
        now = datetime.now(timezone.utc)
        license_in_force = self.licenses.filter(valid_until__gt=now)
        return license_in_force[0] if len(license_in_force) > 0 else None

    def get_license_about_to_expire(self):
        now = datetime.now(timezone.utc)
        filter_datetime = now + timedelta(weeks=2)
        licenses_about_to_expire = self.licenses.filter(valid_until__gt=now, valid_until__lt=filter_datetime)
        return licenses_about_to_expire[0] if len(licenses_about_to_expire) > 0 else None

    def get_license_due_for_payment(self):
        licenses_due_for_payment = self.licenses.filter(valid_until=None)
        return licenses_due_for_payment[0] if len(licenses_due_for_payment) > 0 else None

    def get_account_admins(self):
        account_admins = self.users.filter(is_account_admin=True, is_active=True)
        return account_admins

    def __str__(self):
        return '%s - %s' % (self.company_id, self.name)


class License(models.Model):
    account = models.ForeignKey(Account, related_name='licenses')
    reference_id = models.CharField(max_length=64, blank=True)
    amount = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)
    description = models.TextField(blank=True)
    metadata = models.TextField(blank=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s: %s, from=%s, until=%s" % \
               (self.account.company_id, self.description,
                self.valid_from.strftime('%Y-%m-%d') if self.valid_from else 'N/D',
                self.valid_until.strftime('%Y-%m-%d') if self.valid_until else 'N/D')


class AuthUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, account, email, password, is_staff, is_superuser, **extra_fields):
        now = datetime.now(timezone.utc)

        email = self.normalize_email(email)
        user = self.model(account=account, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          created_at=now, last_login=now, **extra_fields)
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
    account = models.ForeignKey(Account, null=True, blank=True, related_name='users')
    email = models.EmailField(_('email address'), unique=True,
                              help_text=_('Required.'),
                              error_messages={
                                                'unique': _('The given email address has already been registered.')
                                             }
                             )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    metadata = models.TextField(blank=True)

    is_account_admin = models.BooleanField(_('account admin status'), default=False,
                                   help_text=_('Designates whether the user is as account admin.'))

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into the admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    created_at = models.DateTimeField(_('created at'), editable=False)
    updated_at = models.DateTimeField(_('updated at'), editable=False)

    objects = AuthUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

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
            if self.account is not None and len(AuthUser.objects.filter(account=self.account, is_account_admin=True)) == 0:
                self.is_account_admin = True  # an account needs an account admin, so make it the first user to enroll
        else:
            self.updated_at = now
        super(AuthUser, self).save(*args, **kwargs)


class Detector(models.Model):
    TYPE = (
        ('M', 'Movable'),
        ('F', 'Fixed'),
        ('U', 'User'),
    )
    account = models.ForeignKey(Account, related_name='detectors')
    uid = models.CharField(max_length=36)
    reference_id = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=64, blank=True)
    type = models.CharField(max_length=1, choices=TYPE, default='F')
    photo = models.FileField(upload_to='photos', blank=True, null=True)
    location = models.PointField(null=True)
    arrival_rssi = models.IntegerField(default=-85)
    departure_rssi = models.IntegerField(default=-95)
    metadata = models.TextField(blank=True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    is_active = models.BooleanField(default=True)
    objects = models.GeoManager()

    class Meta:
        unique_together = ('account', 'uid', 'reference_id')

    def location_dict(self):
        return {'lat': self.location.latitude, 'lon': self.location.longitude}

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(Detector, self).save(*args, **kwargs)

    def __str__(self):
        return '%s: uid=%s, name=%s' % (self.account.company_id, self.uid, self.name)


class Beacon(models.Model):
    TYPE = (
        ('M', 'Movable'),
        ('F', 'Fixed'),
    )
    account = models.ForeignKey(Account, related_name='beacons')
    uid = models.CharField(max_length=36)
    reference_id = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=64, blank=True)
    type = models.CharField(max_length=1, choices=TYPE, default='M')
    photo = models.FileField(upload_to='photos', blank=True, null=True)
    location = models.PointField(null=True, blank=True)
    reported_missing = models.BooleanField(default=False)
    metadata = models.TextField(blank=True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    is_active = models.BooleanField(default=True)
    objects = models.GeoManager()

    class Meta:
        unique_together = ('account', 'uid', 'reference_id')

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(Beacon, self).save(*args, **kwargs)

    def __str__(self):
        return '%s: uid=%s, type=%s, name=%s' % (self.account.company_id, self.uid, self.type, self.name)


class Sighting(models.Model):
    beacon = models.ForeignKey(Beacon)
    detector = models.ForeignKey(Detector, null=True)
    first_seen_at = models.DateTimeField()
    last_seen_at = models.DateTimeField()
    location = models.PointField(null=True, blank=True)
    rssi = models.IntegerField(null=True, blank=True)
    battery = models.IntegerField(null=True, blank=True)
    metadata = models.TextField(blank=True)
    confirmed = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    confirmed_at = models.DateTimeField(null=True)
    comment = models.TextField(blank=True)
    commented_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    commented_at = models.DateTimeField(null=True)
    is_current = models.BooleanField(default=True)
    objects = models.GeoManager()

    def get_duration(self):
        return (self.last_seen_at - self.first_seen_at).seconds

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            if not self.first_seen_at:
                self.first_seen_at = now
            if not self.last_seen_at:
                self.last_seen_at = now
        else:
            if not self.last_seen_at:
                self.last_seen_at = now
            if self.confirmed and self.confirmed_by and not self.confirmed_at:
                self.confirmed_at = now
            if self.comment and self.commented_by and not self.commented_at:
                self.commented_at = now
        super(Sighting, self).save(*args, **kwargs)

    def __str__(self):
        return "%s: beacon=%s, detector=%s" % (self.id, self.beacon.name, self.detector.name)


class Event(models.Model):
    account = models.ForeignKey(Account)
    reference_id = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=64)
    beacons = models.ManyToManyField(Beacon, blank=True, related_name='events')
    detectors = models.ManyToManyField(Detector, blank=True)

    schedule_days_of_week = models.PositiveSmallIntegerField(default=0)  # used as an 8bit field for easy logical ops
    # schedule_specific_date = models.DateTimeField()
    schedule_start_time = models.TimeField()
    schedule_end_time = models.TimeField()
    schedule_timezone_offset = models.SmallIntegerField(default=0)

    sighting_is_current = models.BooleanField(default=False)
    sighting_duration_in_seconds = models.IntegerField(default=0)
    sighting_has_battery_below = models.IntegerField(default=100)
    sighting_has_comment = models.NullBooleanField(default=None)
    sighting_has_been_confirmed = models.NullBooleanField(default=None)
    sighting_previous_event = models.ForeignKey('Event', null=True)

    metadata = models.TextField(blank=True) # event actions: Notification, SMS, Email, REST call
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return "%s: reference_id=%s, name=%s)" % (self.account.company_id, self.reference_id, self.name)


class EventOccurrence(models.Model):
    event = models.ForeignKey(Event)
    sighting = models.ForeignKey(Sighting)
    occurred_at = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.occurred_at = now
        super(EventOccurrence, self).save(*args, **kwargs)

    def __str__(self):
        return "%s: event_reference_id=%s, occurred_at=%s" % \
               (self.event.account.company_id, self.event.reference_id, self.occurred_at)


class EventLimit(models.Model):
    reference_id = models.CharField(max_length=64, blank=True)
    event = models.ForeignKey(Event)
    beacon = models.ForeignKey(Beacon, null=True)
    occurrence_date_start_limit = models.DateTimeField()
    occurrence_date_end_limit = models.DateTimeField(blank=True, null=True)
    occurrence_count_limit = models.IntegerField(default=-1)

    metadata = models.TextField(blank=True) # event limit actions: Notification, SMS, Email, REST call
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(EventLimit, self).save(*args, **kwargs)

    def __str__(self):
        return "%s: reference_id=%s" % (self.event.account.company_id, self.reference_id)


class Notification(models.Model):
    account = models.ForeignKey(Account)
    metadata = models.TextField(blank=True)  # populated with title, category and message by event occurrence / limit actions
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='+')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        if not self.id:
            self.created_at = now
            self.updated_at = now
        else:
            self.updated_at = now
        super(Notification, self).save(*args, **kwargs)