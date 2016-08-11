# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0007_auto_20160719_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detector',
            name='type',
            field=models.CharField(max_length=1, choices=[('M', 'Movable'), ('F', 'Fixed')], default='F'),
        ),
    ]
