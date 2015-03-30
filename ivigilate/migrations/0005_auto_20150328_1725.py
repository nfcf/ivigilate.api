# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0004_auto_20150324_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sighting',
            name='first_seen_at',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sighting',
            name='last_seen_at',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
