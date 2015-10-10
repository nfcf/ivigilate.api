# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0020_auto_20151010_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventlimit',
            name='account',
            field=models.ForeignKey(default=10, to='ivigilate.Account'),
            preserve_default=False,
        ),
    ]
