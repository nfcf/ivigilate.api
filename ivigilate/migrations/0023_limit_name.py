# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0022_auto_20151011_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='limit',
            name='name',
            field=models.CharField(max_length=64, default=''),
            preserve_default=False,
        ),
    ]
