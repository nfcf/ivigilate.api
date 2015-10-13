# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields
from django.conf import settings
import ivigilate.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('email', models.EmailField(error_messages={'unique': 'The given email address has already been registered.'}, max_length=254, help_text='Required.', unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('metadata', models.TextField(blank=True)),
                ('is_account_admin', models.BooleanField(default=False, verbose_name='account admin status', help_text='Designates whether the user is as account admin.')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status', help_text='Designates whether the user can log into the admin site.')),
                ('is_active', models.BooleanField(default=True, verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('created_at', models.DateTimeField(verbose_name='created at', editable=False)),
                ('updated_at', models.DateTimeField(verbose_name='updated at', editable=False)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', ivigilate.models.AuthUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('company_id', models.CharField(max_length=32, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Beacon',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('uid', models.CharField(max_length=36)),
                ('reference_id', models.CharField(max_length=64, blank=True)),
                ('name', models.CharField(max_length=64, blank=True)),
                ('type', models.CharField(default='M', max_length=1, choices=[('M', 'Movable'), ('F', 'Fixed')])),
                ('photo', models.FileField(null=True, upload_to='photos', blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, blank=True, srid=4326)),
                ('reported_missing', models.BooleanField(default=False)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account', related_name='beacons')),
                ('updated_by', models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Detector',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('uid', models.CharField(max_length=36)),
                ('reference_id', models.CharField(max_length=64, blank=True)),
                ('name', models.CharField(max_length=64, blank=True)),
                ('type', models.CharField(default='F', max_length=1, choices=[('M', 'Movable'), ('F', 'Fixed'), ('U', 'User')])),
                ('photo', models.FileField(null=True, upload_to='photos', blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('arrival_rssi', models.IntegerField(default=-85)),
                ('departure_rssi', models.IntegerField(default=-95)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account', related_name='detectors')),
                ('updated_by', models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
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
                ('beacons', models.ManyToManyField(blank=True, to='ivigilate.Beacon', related_name='events')),
                ('detectors', models.ManyToManyField(blank=True, to='ivigilate.Detector')),
                ('updated_by', models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventOccurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('occurred_at', models.DateTimeField(editable=False)),
                ('event', models.ForeignKey(to='ivigilate.Event')),
            ],
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('reference_id', models.CharField(max_length=64, blank=True)),
                ('amount', models.PositiveIntegerField()),
                ('currency', models.CharField(max_length=3)),
                ('description', models.TextField(blank=True)),
                ('metadata', models.TextField(blank=True)),
                ('valid_from', models.DateTimeField(null=True, blank=True)),
                ('valid_until', models.DateTimeField(null=True, blank=True)),
                ('account', models.ForeignKey(to='ivigilate.Account', related_name='licenses')),
            ],
        ),
        migrations.CreateModel(
            name='Limit',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('reference_id', models.CharField(max_length=64, blank=True)),
                ('name', models.CharField(max_length=64)),
                ('start_date', models.DateTimeField()),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('beacons', models.ManyToManyField(blank=True, to='ivigilate.Beacon', related_name='limits')),
                ('events', models.ManyToManyField(blank=True, to='ivigilate.Event', related_name='limits')),
                ('updated_by', models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LimitOccurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('occurred_at', models.DateTimeField(editable=False)),
                ('beacon', models.ForeignKey(to='ivigilate.Beacon')),
                ('event', models.ForeignKey(to='ivigilate.Event')),
                ('limit', models.ForeignKey(to='ivigilate.Limit')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('updated_by', models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sighting',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('first_seen_at', models.DateTimeField()),
                ('last_seen_at', models.DateTimeField()),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, blank=True, srid=4326)),
                ('rssi', models.IntegerField(null=True, blank=True)),
                ('battery', models.IntegerField(null=True, blank=True)),
                ('metadata', models.TextField(blank=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('confirmed_at', models.DateTimeField(null=True)),
                ('comment', models.TextField(blank=True)),
                ('commented_at', models.DateTimeField(null=True)),
                ('is_current', models.BooleanField(default=True)),
                ('beacon', models.ForeignKey(to='ivigilate.Beacon')),
                ('commented_by', models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL)),
                ('confirmed_by', models.ForeignKey(related_name='+', null=True, to=settings.AUTH_USER_MODEL)),
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
            field=models.ForeignKey(related_name='users', null=True, blank=True, to='ivigilate.Account'),
        ),
        migrations.AddField(
            model_name='authuser',
            name='groups',
            field=models.ManyToManyField(verbose_name='groups', to='auth.Group', related_name='user_set', related_query_name='user', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        ),
        migrations.AddField(
            model_name='authuser',
            name='user_permissions',
            field=models.ManyToManyField(verbose_name='user permissions', to='auth.Permission', related_name='user_set', related_query_name='user', blank=True, help_text='Specific permissions for this user.'),
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
