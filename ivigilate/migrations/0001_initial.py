# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import geoposition.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('email', models.EmailField(error_messages={'unique': 'The given email address has already been registered.'}, verbose_name='email address', max_length=75, help_text='Required.', unique=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('metadata', models.TextField(blank=True)),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status', help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='created at')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='updated at')),
            ],
            options={
                'verbose_name_plural': 'settings',
                'verbose_name': 'user',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('company_id', models.CharField(max_length=32, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('reference_id', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventAction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('type', models.CharField(choices=[('T', 'Trigger'), ('L', 'Limit')], max_length=1)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('event', models.ForeignKey(to='ivigilate.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventLimit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('occurrence_date_limit', models.DateTimeField()),
                ('occurrence_count_limit', models.IntegerField()),
                ('occurrence_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('event', models.ForeignKey(to='ivigilate.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventOccurrence',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('duration', models.TimeField()),
                ('occurred_at', models.DateTimeField(editable=False)),
                ('event', models.ForeignKey(to='ivigilate.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventTrigger',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('is_occurring_after_X_seconds_since_last', models.IntegerField(default=0)),
                ('is_going_on_for_longer_than_X_seconds', models.IntegerField(default=0)),
                ('is_closed', models.BooleanField(default=False)),
                ('has_battery_level_below', models.IntegerField(default=0)),
                ('has_comment', models.BooleanField(default=False)),
                ('occurred_in_at_least_X_places', models.IntegerField(default=0)),
                ('event', models.ForeignKey(to='ivigilate.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('type', models.CharField(choices=[('SAM', 'School Attendance Management'), ('EAM', 'Event Attendance Management'), ('SAC', 'Simple Attendance Control'), ('AC', 'Absence Control'), ('LF', 'Lost & Found')], max_length=3)),
                ('max_movables', models.IntegerField()),
                ('max_users', models.IntegerField()),
                ('metadata', models.TextField(blank=True)),
                ('valid_from', models.DateTimeField()),
                ('valid_until', models.DateTimeField(null=True, blank=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Movable',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('uuid', models.CharField(max_length=36, unique=True)),
                ('reference_id', models.CharField(max_length=64)),
                ('photo', models.ImageField(upload_to='photos')),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('type', models.CharField(choices=[('B', 'Beacon'), ('W', 'Watcher'), ('BW', 'Beacon & Watcher')], max_length=2)),
                ('arrival_rssi', models.IntegerField(default=-75)),
                ('departure_rssi', models.IntegerField(default=-90)),
                ('metadata', models.TextField(blank=True)),
                ('reported_missing', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('event_limits', models.ManyToManyField(through='ivigilate.EventLimit', to='ivigilate.Event', related_name='+')),
                ('event_occurrences', models.ManyToManyField(through='ivigilate.EventOccurrence', to='ivigilate.Event', related_name='+')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('uuid', models.CharField(max_length=36, unique=True)),
                ('reference_id', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('location', geoposition.fields.GeopositionField(max_length=42)),
                ('arrival_rssi', models.IntegerField(default=-75)),
                ('departure_rssi', models.IntegerField(default=-90)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('group_id', models.CharField(max_length=64)),
                ('reference_id', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('starts_at', models.DateTimeField()),
                ('ends_at', models.DateTimeField()),
                ('metadata', models.TextField(blank=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('events', models.ManyToManyField(to='ivigilate.Event')),
                ('movables', models.ManyToManyField(to='ivigilate.Movable')),
                ('places', models.ManyToManyField(to='ivigilate.Place')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sighting',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('watcher_id', models.CharField(db_index=True, max_length=32)),
                ('first_seen_at', models.DateTimeField(editable=False)),
                ('last_seen_at', models.DateTimeField(editable=False)),
                ('location', geoposition.fields.GeopositionField(max_length=42)),
                ('rssi', models.IntegerField()),
                ('battery_level', models.IntegerField()),
                ('metadata', models.TextField(blank=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('confirmed_at', models.DateTimeField(null=True)),
                ('comment', models.TextField()),
                ('commented_at', models.DateTimeField(null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('commented_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+')),
                ('confirmed_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+')),
                ('movable', models.ForeignKey(to='ivigilate.Movable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='schedule',
            name='sightings',
            field=models.ManyToManyField(to='ivigilate.Sighting'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventtrigger',
            name='movable',
            field=models.ForeignKey(to='ivigilate.Movable', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventoccurrence',
            name='movable',
            field=models.ForeignKey(to='ivigilate.Movable'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventoccurrence',
            name='places',
            field=models.ManyToManyField(to='ivigilate.Place'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventlimit',
            name='movable',
            field=models.ForeignKey(to='ivigilate.Movable'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authuser',
            name='account',
            field=models.ForeignKey(null=True, blank=True, to='ivigilate.Account'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', to='auth.Group', related_query_name='user', verbose_name='groups', related_name='user_set'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', to='auth.Permission', related_query_name='user', verbose_name='user permissions', related_name='user_set'),
            preserve_default=True,
        ),
    ]
