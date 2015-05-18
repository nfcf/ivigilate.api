# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0026_auto_20150515_0827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='license',
            name='amount',
            field=models.PositiveIntegerField(),
            preserve_default=True,
        ),
    ]
