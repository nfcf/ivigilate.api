# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0021_eventlimit_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='Limit',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('reference_id', models.CharField(blank=True, max_length=64)),
                ('start_date', models.DateTimeField()),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(to='ivigilate.Account')),
                ('beacons', models.ManyToManyField(related_name='event_limits', to='ivigilate.Beacon', blank=True)),
                ('events', models.ManyToManyField(related_name='event_limits', to='ivigilate.Event', blank=True)),
                ('updated_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='+')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LimitOccurrence',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('occurred_at', models.DateTimeField(editable=False)),
                ('beacon', models.ForeignKey(to='ivigilate.Beacon')),
                ('limit', models.ForeignKey(to='ivigilate.Limit')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='eventlimit',
            name='account',
        ),
        migrations.RemoveField(
            model_name='eventlimit',
            name='beacons',
        ),
        migrations.RemoveField(
            model_name='eventlimit',
            name='events',
        ),
        migrations.RemoveField(
            model_name='eventlimit',
            name='updated_by',
        ),
        migrations.DeleteModel(
            name='EventLimit',
        ),
    ]
