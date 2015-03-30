# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0007_event_period_in_seconds_to_check'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='movables',
            field=models.ManyToManyField(to='ivigilate.Movable', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='places',
            field=models.ManyToManyField(to='ivigilate.Place', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='reference_id',
            field=models.CharField(blank=True, max_length=64),
            preserve_default=True,
        ),
    ]
