# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0024_auto_20151012_1216'),
    ]

    operations = [
        migrations.AddField(
            model_name='limitoccurrence',
            name='event',
            field=models.ForeignKey(default=14, to='ivigilate.Event'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='limit',
            name='beacons',
            field=models.ManyToManyField(to='ivigilate.Beacon', related_name='limits', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='limit',
            name='events',
            field=models.ManyToManyField(to='ivigilate.Event', related_name='limits', blank=True),
            preserve_default=True,
        ),
    ]
