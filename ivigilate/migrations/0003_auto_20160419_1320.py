# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0002_notification_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='beacons',
        ),
        migrations.AddField(
            model_name='event',
            name='authorized_beacons',
            field=models.ManyToManyField(to='ivigilate.Beacon', related_name='authorized_events', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='unauthorized_beacons',
            field=models.ManyToManyField(to='ivigilate.Beacon', related_name='unauthorized_events', blank=True),
        ),
    ]
