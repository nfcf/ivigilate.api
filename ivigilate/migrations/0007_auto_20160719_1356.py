# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0006_auto_20160624_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sighting',
            name='beacon',
            field=models.ForeignKey(to='ivigilate.Beacon', null=True),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='detector',
            field=models.ForeignKey(to='ivigilate.Detector'),
        ),
        migrations.AlterField(
            model_name='sighting',
            name='type',
            field=models.CharField(max_length=3, choices=[('AC', 'AutoClosing'), ('MC', 'ManualClosing'), ('GPS', 'GPS')], default='AC'),
        ),
    ]
