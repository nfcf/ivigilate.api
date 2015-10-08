# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0017_remove_eventoccurrence_beacon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventlimit',
            name='beacon',
        ),
        migrations.AddField(
            model_name='eventlimit',
            name='beacons',
            field=models.ManyToManyField(to='ivigilate.Beacon', blank=True, related_name='event_limits'),
            preserve_default=True,
        ),
    ]
