# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0015_auto_20151005_0837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventlimit',
            name='occurrence_date_limit',
        ),
        migrations.AddField(
            model_name='eventlimit',
            name='occurrence_date_end_limit',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventlimit',
            name='occurrence_date_start_limit',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 6, 7, 26, 26, 449545, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
