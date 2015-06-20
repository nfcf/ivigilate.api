# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0006_auto_20150620_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='authuser',
            name='reference_id',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
    ]
