# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0011_auto_20151003_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='account',
            field=models.ForeignKey(to='ivigilate.Account', default=10),
            preserve_default=False,
        ),
    ]
