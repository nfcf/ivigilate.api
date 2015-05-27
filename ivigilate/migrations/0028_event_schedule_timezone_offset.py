# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0027_auto_20150515_0858'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='schedule_timezone_offset',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
