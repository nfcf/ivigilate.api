# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0018_auto_20150505_0807'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='sighting_previous_event',
            field=models.ForeignKey(null=True, to='ivigilate.Event'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventoccurrence',
            name='event',
            field=models.ForeignKey(to='ivigilate.Event'),
            preserve_default=True,
        ),
    ]
