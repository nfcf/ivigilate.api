# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ivigilate.models
import django.contrib.gis.db.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('email', models.EmailField(help_text='Required.', max_length=254, error_messages={'unique': 'The given email address has already been registered.'}, verbose_name='email address', unique=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('metadata', models.TextField(blank=True)),
                ('is_account_admin', models.BooleanField(help_text='Designates whether the user is as account admin.', default=False, verbose_name='account admin status')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into the admin site.', default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='created at')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='updated at')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            managers=[
                ('objects', ivigilate.models.AuthUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('company_id', models.CharField(max_length=32, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Beacon',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('uid', models.CharField(max_length=36)),
                ('reference_id', models.CharField(max_length=64, blank=True)),
                ('name', models.CharField(max_length=64, blank=True)),
                ('type', models.CharField(default='M', choices=[('M', 'Movable'), ('F', 'Fixed')], max_length=1)),
                ('photo', models.FileField(null=True, upload_to='photos', blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326, blank=True)),
                ('reported_missing', models.BooleanField(default=False)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(related_name='beacons', to='ivigilate.Account')),
                ('updated_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Detector',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('uid', models.CharField(max_length=36)),
                ('reference_id', models.CharField(max_length=64, blank=True)),
                ('name', models.CharField(max_length=64, blank=True)),
                ('type', models.CharField(default='F', choices=[('M', 'Movable'), ('F', 'Fixed'), ('U', 'User')], max_length=1)),
                ('photo', models.FileField(null=True, upload_to='photos', blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('arrival_rssi', models.IntegerField(default=-85)),
                ('departure_rssi', models.IntegerField(default=-95)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(related_name='detectors', to='ivigilate.Account')),
                ('updated_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('reference_id', models.CharField(max_length=64, blank=True)),
                ('name', models.CharField(max_length=64)),
                ('schedule_days_of_week', models.PositiveSmallIntegerField(default=0)),
                ('schedule_start_time', models.TimeField()),
                ('schedule_end_time', models.TimeField()),
                ('schedule_timezone_offset', models.SmallIntegerField(default=0)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('beacons', models.ManyToManyField(related_name='events', to='ivigilate.Beacon', blank=True)),
                ('detectors', models.ManyToManyField(to='ivigilate.Detector', blank=True)),
                ('updated_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventOccurrence',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('occurred_at', models.DateTimeField(editable=False)),
                ('event', models.ForeignKey(to='ivigilate.Event')),
            ],
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('reference_id', models.CharField(max_length=64, blank=True)),
                ('amount', models.PositiveIntegerField()),
                ('currency', models.CharField(max_length=3)),
                ('description', models.TextField(blank=True)),
                ('metadata', models.TextField(blank=True)),
                ('valid_from', models.DateTimeField(null=True, blank=True)),
                ('valid_until', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('account', models.ForeignKey(related_name='licenses', to='ivigilate.Account')),
                ('updated_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Limit',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('reference_id', models.CharField(max_length=64, blank=True)),
                ('name', models.CharField(max_length=64)),
                ('start_date', models.DateTimeField()),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('beacons', models.ManyToManyField(related_name='limits', to='ivigilate.Beacon', blank=True)),
                ('events', models.ManyToManyField(related_name='limits', to='ivigilate.Event', blank=True)),
                ('updated_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LimitOccurrence',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('occurred_at', models.DateTimeField(editable=False)),
                ('beacon', models.ForeignKey(to='ivigilate.Beacon')),
                ('event', models.ForeignKey(to='ivigilate.Event')),
                ('limit', models.ForeignKey(to='ivigilate.Limit')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('updated_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sighting',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('first_seen_at', models.DateTimeField()),
                ('last_seen_at', models.DateTimeField()),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326, blank=True)),
                ('rssi', models.IntegerField(null=True, blank=True)),
                ('battery', models.IntegerField(null=True, blank=True)),
                ('metadata', models.TextField(blank=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('confirmed_at', models.DateTimeField(null=True)),
                ('comment', models.TextField(blank=True)),
                ('commented_at', models.DateTimeField(null=True)),
                ('is_current', models.BooleanField(default=True)),
                ('beacon', models.ForeignKey(to='ivigilate.Beacon')),
                ('commented_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('confirmed_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('detector', models.ForeignKey(null=True, to='ivigilate.Detector')),
            ],
        ),
        migrations.AddField(
            model_name='eventoccurrence',
            name='sighting',
            field=models.ForeignKey(to='ivigilate.Sighting'),
        ),
        migrations.AddField(
            model_name='authuser',
            name='account',
            field=models.ForeignKey(blank=True, null=True, related_name='users', to='ivigilate.Account'),
        ),
        migrations.AddField(
            model_name='authuser',
            name='groups',
            field=models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group', blank=True, related_query_name='user', related_name='user_set', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='authuser',
            name='user_permissions',
            field=models.ManyToManyField(help_text='Specific permissions for this user.', to='auth.Permission', blank=True, related_query_name='user', related_name='user_set', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='detector',
            unique_together=set([('account', 'uid', 'reference_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='beacon',
            unique_together=set([('account', 'uid', 'reference_id')]),
        ),
    ]
