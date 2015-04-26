# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0014_auto_20150426_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='sighting_has_been_confirmed',
            field=models.NullBooleanField(default=None),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='sighting_has_comment',
            field=models.NullBooleanField(default=None),
            preserve_default=True,
        ),
    ]
