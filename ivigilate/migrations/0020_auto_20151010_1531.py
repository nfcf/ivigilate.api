# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0019_event_dormant_period_in_seconds'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventlimit',
            name='event',
        ),
        migrations.AddField(
            model_name='eventlimit',
            name='events',
            field=models.ManyToManyField(related_name='event_limits', to='ivigilate.Event', blank=True),
            preserve_default=True,
        ),
    ]
