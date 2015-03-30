# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0006_auto_20150330_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='period_in_seconds_to_check',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
