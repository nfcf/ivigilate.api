# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0003_auto_20160419_1320'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sighting',
            old_name='battery',
            new_name='beacon_battery',
        ),
        migrations.AddField(
            model_name='sighting',
            name='detector_battery',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
