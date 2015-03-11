# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0008_auto_20150310_1913'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sighting',
            old_name='is_active',
            new_name='is_current',
        ),
    ]
