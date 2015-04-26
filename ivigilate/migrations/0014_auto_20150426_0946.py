# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0013_auto_20150424_0845'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='sighting_is_confirmed',
        ),
        migrations.AddField(
            model_name='event',
            name='sighting_has_been_confirmed',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='sighting_has_battery_below',
            field=models.IntegerField(default=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='sighting_has_comment',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
