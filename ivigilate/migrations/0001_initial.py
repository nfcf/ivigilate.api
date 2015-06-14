# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.contrib.gis.db.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.', default=False)),
                ('email', models.EmailField(unique=True, error_messages={'unique': 'The given email address has already been registered.'}, verbose_name='email address', help_text='Required.', max_length=75)),
                ('first_name', models.CharField(verbose_name='first name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', blank=True, max_length=30)),
                ('metadata', models.TextField(blank=True)),
                ('is_account_admin', models.BooleanField(verbose_name='account admin status', help_text='Designates whether the user is as account admin.', default=False)),
                ('is_staff', models.BooleanField(verbose_name='staff status', help_text='Designates whether the user can log into the admin site.', default=False)),
                ('is_active', models.BooleanField(verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True)),
                ('created_at', models.DateTimeField(editable=False, verbose_name='created at')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='updated at')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('company_id', models.CharField(unique=True, max_length=32)),
                ('name', models.CharField(max_length=64)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Beacon',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('uid', models.CharField(max_length=36)),
                ('reference_id', models.CharField(blank=True, max_length=64)),
                ('type', models.CharField(choices=[('M', 'Movable'), ('F', 'Fixed')], max_length=1, default='M')),
                ('name', models.CharField(blank=True, max_length=64)),
                ('photo', models.FileField(blank=True, null=True, upload_to='photos')),
                ('reported_missing', models.BooleanField(default=False)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(related_name='beacons', to='ivigilate.Account')),
                ('updated_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('reference_id', models.CharField(blank=True, max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('schedule_days_of_week', models.PositiveSmallIntegerField(default=0)),
                ('schedule_start_time', models.TimeField()),
                ('schedule_end_time', models.TimeField()),
                ('schedule_timezone_offset', models.SmallIntegerField(default=0)),
                ('sighting_is_current', models.BooleanField(default=False)),
                ('sighting_duration_in_seconds', models.IntegerField(default=0)),
                ('sighting_has_battery_below', models.IntegerField(default=100)),
                ('sighting_has_comment', models.NullBooleanField(default=None)),
                ('sighting_has_been_confirmed', models.NullBooleanField(default=None)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('beacons', models.ManyToManyField(related_name='events', to='ivigilate.Beacon', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventLimit',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('occurrence_date_limit', models.DateTimeField()),
                ('occurrence_count_limit', models.IntegerField()),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('beacon', models.ForeignKey(to='ivigilate.Beacon')),
                ('event', models.ForeignKey(to='ivigilate.Event')),
                ('updated_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventOccurrence',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('occurred_at', models.DateTimeField(editable=False)),
                ('beacon', models.ForeignKey(to='ivigilate.Beacon')),
                ('event', models.ForeignKey(to='ivigilate.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('reference_id', models.CharField(blank=True, max_length=64)),
                ('amount', models.PositiveIntegerField()),
                ('currency', models.CharField(max_length=3)),
                ('description', models.TextField(blank=True)),
                ('metadata', models.TextField(blank=True)),
                ('valid_from', models.DateTimeField(blank=True, null=True)),
                ('valid_until', models.DateTimeField(blank=True, null=True)),
                ('account', models.ForeignKey(related_name='licenses', to='ivigilate.Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('uid', models.CharField(max_length=36)),
                ('reference_id', models.CharField(blank=True, max_length=64)),
                ('name', models.CharField(blank=True, max_length=64)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True)),
                ('arrival_rssi', models.IntegerField(default=-75)),
                ('departure_rssi', models.IntegerField(default=-90)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(related_name='places', to='ivigilate.Account')),
                ('updated_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sighting',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('first_seen_at', models.DateTimeField()),
                ('last_seen_at', models.DateTimeField()),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, blank=True, null=True)),
                ('rssi', models.IntegerField(blank=True, null=True)),
                ('battery', models.IntegerField(blank=True, null=True)),
                ('metadata', models.TextField(blank=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('confirmed_at', models.DateTimeField(null=True)),
                ('comment', models.TextField(blank=True)),
                ('commented_at', models.DateTimeField(null=True)),
                ('is_current', models.BooleanField(default=True)),
                ('beacon', models.ForeignKey(to='ivigilate.Beacon')),
                ('commented_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('confirmed_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('place', models.ForeignKey(to='ivigilate.Place', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('account', 'uid', 'reference_id')]),
        ),
        migrations.AddField(
            model_name='eventoccurrence',
            name='sighting',
            field=models.ForeignKey(to='ivigilate.Sighting'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='places',
            field=models.ManyToManyField(to='ivigilate.Place', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='sighting_previous_event',
            field=models.ForeignKey(to='ivigilate.Event', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='updated_by',
            field=models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='beacon',
            unique_together=set([('account', 'uid', 'reference_id')]),
        ),
        migrations.AddField(
            model_name='authuser',
            name='account',
            field=models.ForeignKey(null=True, blank=True, related_name='users', to='ivigilate.Account'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authuser',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', blank=True, related_name='user_set', to='auth.Group', verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authuser',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', blank=True, related_name='user_set', to='auth.Permission', verbose_name='user permissions', help_text='Specific permissions for this user.'),
            preserve_default=True,
        ),
    ]
