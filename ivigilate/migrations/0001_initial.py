# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('email', models.EmailField(help_text='Required.', max_length=75, unique=True, error_messages={'unique': 'The given email address has already been registered.'}, verbose_name='email address')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('metadata', models.TextField(blank=True)),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('reference_id', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('updated_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventAction',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('type', models.CharField(max_length=1, choices=[('T', 'Trigger'), ('L', 'Limit')])),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('type', models.CharField(max_length=3, choices=[('SAM', 'School Attendance Management'), ('EAM', 'Event Attendance Management'), ('SAC', 'Simple Attendance Control'), ('AC', 'Absence Control'), ('LF', 'Lost & Found')])),
                ('max_movables', models.IntegerField()),
                ('max_users', models.IntegerField()),
                ('metadata', models.TextField(blank=True)),
                ('valid_from', models.DateTimeField()),
                ('valid_until', models.DateTimeField(null=True, blank=True)),
                ('account', models.ForeignKey(to='ivigilate.Account', related_name='licenses')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Movable',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uid', models.CharField(max_length=36, unique=True)),
                ('reference_id', models.CharField(blank=True, max_length=64)),
                ('photo', models.FileField(null=True, blank=True, upload_to='photos')),
                ('name', models.CharField(blank=True, max_length=64)),
                ('arrival_rssi', models.IntegerField(blank=True, default=-75)),
                ('departure_rssi', models.IntegerField(blank=True, default=-90)),
                ('metadata', models.TextField(blank=True)),
                ('reported_missing', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('event_limits', models.ManyToManyField(through='ivigilate.EventLimit', to='ivigilate.Event', related_name='+')),
                ('event_occurrences', models.ManyToManyField(through='ivigilate.EventOccurrence', to='ivigilate.Event', related_name='+')),
                ('updated_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uid', models.CharField(max_length=36)),
                ('reference_id', models.CharField(blank=True, max_length=64)),
                ('name', models.CharField(blank=True, max_length=64)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('arrival_rssi', models.IntegerField(default=-75)),
                ('departure_rssi', models.IntegerField(default=-90)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('updated_by', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('watcher_uid', models.CharField(max_length=36, db_index=True)),
                ('first_seen_at', models.DateTimeField(editable=False)),
                ('last_seen_at', models.DateTimeField(editable=False)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('rssi', models.IntegerField(null=True, blank=True)),
                ('battery', models.IntegerField(null=True, blank=True)),
                ('metadata', models.TextField(blank=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('confirmed_at', models.DateTimeField(null=True)),
                ('comment', models.TextField(blank=True)),
                ('commented_at', models.DateTimeField(null=True)),
                ('is_current', models.BooleanField(default=True)),
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
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('account', 'uid')]),
        ),
        migrations.AddField(
            model_name='eventtrigger',
            name='movable',
            field=models.ForeignKey(null=True, to='ivigilate.Movable'),
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
            field=models.ManyToManyField(blank=True, related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', to='auth.Group', related_name='user_set', verbose_name='groups'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, related_query_name='user', help_text='Specific permissions for this user.', to='auth.Permission', related_name='user_set', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
