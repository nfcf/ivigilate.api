# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0009_auto_20150330_2238'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='trigger_duration_in_seconds',
            new_name='sighting_duration_in_seconds',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='trigger_has_battery_level_below',
            new_name='sighting_has_battery_level_below',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='trigger_has_comment',
            new_name='sighting_has_comment',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='trigger_is_current',
            new_name='sighting_is_current',
        ),
    ]
