# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0004_auto_20160427_1206'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sighting',
            old_name='is_current',
            new_name='is_active',
        ),
        migrations.AddField(
            model_name='sighting',
            name='type',
            field=models.CharField(default='A', max_length=1, choices=[('A', 'AutoClosing'), ('M', 'ManualClosing')]),
        ),
    ]
