# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='event',
            field=models.ForeignKey(to='ivigilate.Event', null=True),
        ),
    ]
