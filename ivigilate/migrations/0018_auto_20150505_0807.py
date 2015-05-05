# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0017_auto_20150502_1905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventoccurrence',
            name='event',
            field=models.ForeignKey(related_name='sighting_previous_event_occurrence', to='ivigilate.Event'),
            preserve_default=True,
        ),
    ]
