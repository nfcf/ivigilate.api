# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0006_auto_20150308_0851'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sighting',
            old_name='battery_level',
            new_name='battery',
        ),
    ]
