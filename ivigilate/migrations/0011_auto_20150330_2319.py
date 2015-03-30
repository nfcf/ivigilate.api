# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0010_auto_20150330_2239'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='sighting_has_battery_level_below',
            new_name='sighting_has_battery_below',
        ),
    ]
