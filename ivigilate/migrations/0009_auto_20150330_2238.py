# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0008_auto_20150330_1902'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='period_in_seconds_to_check',
            new_name='trigger_duration_in_seconds',
        ),
        migrations.AddField(
            model_name='event',
            name='trigger_has_battery_level_below',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='trigger_has_comment',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='trigger_is_current',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
