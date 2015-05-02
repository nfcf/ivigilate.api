# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0016_event_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='movables',
            field=models.ManyToManyField(related_name='events', to='ivigilate.Movable', blank=True),
            preserve_default=True,
        ),
    ]
