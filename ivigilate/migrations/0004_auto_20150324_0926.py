# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0003_auto_20150322_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sighting',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, srid=4326, null=True),
            preserve_default=True,
        ),
    ]
