# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0007_auto_20150308_0917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sighting',
            name='battery',
            field=models.IntegerField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sighting',
            name='rssi',
            field=models.IntegerField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
