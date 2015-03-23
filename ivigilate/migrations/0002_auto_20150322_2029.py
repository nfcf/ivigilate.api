# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movable',
            name='arrival_rssi',
        ),
        migrations.RemoveField(
            model_name='movable',
            name='departure_rssi',
        ),
    ]
