# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0025_license_reference_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='license',
            name='amount',
            field=models.DecimalField(default=200.0, decimal_places=2, max_digits=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='license',
            name='currency',
            field=models.CharField(default='EUR', max_length=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='license',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
