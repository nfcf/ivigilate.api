# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0005_auto_20160427_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sighting',
            name='type',
            field=models.CharField(max_length=2, choices=[('AC', 'AutoClosing'), ('MC', 'ManualClosing')], default='AC'),
        ),
    ]
