# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import geoposition.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='license',
            name='account',
            field=models.ForeignKey(to='ivigilate.Account', related_name='licenses'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='place',
            name='location',
            field=geoposition.fields.GeopositionField(max_length=42, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sighting',
            name='watcher_uid',
            field=models.CharField(max_length=36, db_index=True),
            preserve_default=True,
        ),
    ]
