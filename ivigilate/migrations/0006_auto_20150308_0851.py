# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0005_auto_20150307_2124'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='authuser',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.RemoveField(
            model_name='movable',
            name='type',
        ),
    ]
