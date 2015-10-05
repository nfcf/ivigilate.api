# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0013_eventlimit_reference_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlimit',
            name='occurrence_count_limit',
            field=models.IntegerField(default=-1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventlimit',
            name='occurrence_date_limit',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
