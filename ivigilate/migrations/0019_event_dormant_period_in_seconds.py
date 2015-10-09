# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0018_auto_20151007_2350'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='dormant_period_in_seconds',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
