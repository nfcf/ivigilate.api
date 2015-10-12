# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0023_limit_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='dormant_period_in_seconds',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sighting_duration_in_seconds',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sighting_has_battery_below',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sighting_has_been_confirmed',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sighting_has_comment',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sighting_is_current',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sighting_previous_event',
        ),
    ]
