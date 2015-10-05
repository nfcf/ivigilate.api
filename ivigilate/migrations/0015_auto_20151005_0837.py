# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0014_auto_20151005_0814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlimit',
            name='beacon',
            field=models.ForeignKey(to='ivigilate.Beacon', null=True),
            preserve_default=True,
        ),
    ]
