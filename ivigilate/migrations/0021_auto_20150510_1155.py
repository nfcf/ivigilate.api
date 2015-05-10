# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0020_auto_20150510_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='license',
            name='valid_from',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
