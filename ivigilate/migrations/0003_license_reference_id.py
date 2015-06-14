# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0002_remove_license_reference_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='license',
            name='reference_id',
            field=models.CharField(blank=True, max_length=64),
            preserve_default=True,
        ),
    ]
