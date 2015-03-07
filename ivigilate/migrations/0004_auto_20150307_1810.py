# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0003_auto_20150307_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sighting',
            name='comment',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
