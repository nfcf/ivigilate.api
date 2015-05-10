# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0019_auto_20150506_0914'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='license',
            name='max_movables',
        ),
        migrations.RemoveField(
            model_name='license',
            name='max_users',
        ),
        migrations.RemoveField(
            model_name='license',
            name='type',
        ),
        migrations.AlterField(
            model_name='event',
            name='sighting_is_current',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
