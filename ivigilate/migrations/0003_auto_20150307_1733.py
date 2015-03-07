# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0002_auto_20150307_1224'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movable',
            old_name='uuid',
            new_name='uid',
        ),
        migrations.RenameField(
            model_name='place',
            old_name='uuid',
            new_name='uid',
        ),
        migrations.AlterField(
            model_name='movable',
            name='arrival_rssi',
            field=models.IntegerField(default=-75, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='movable',
            name='departure_rssi',
            field=models.IntegerField(default=-90, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='movable',
            name='first_name',
            field=models.CharField(blank=True, max_length=64),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='movable',
            name='last_name',
            field=models.CharField(blank=True, max_length=64),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='movable',
            name='photo',
            field=models.ImageField(null=True, upload_to='photos', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='movable',
            name='reference_id',
            field=models.CharField(blank=True, max_length=64),
            preserve_default=True,
        ),
    ]
