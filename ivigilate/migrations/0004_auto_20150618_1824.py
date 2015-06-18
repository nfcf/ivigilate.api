# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0003_license_reference_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='beacon',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='place',
            name='arrival_rssi',
            field=models.IntegerField(default=-85),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='place',
            name='departure_rssi',
            field=models.IntegerField(default=-95),
            preserve_default=True,
        ),
    ]
