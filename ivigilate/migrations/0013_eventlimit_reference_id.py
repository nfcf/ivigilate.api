# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0012_notification_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventlimit',
            name='reference_id',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
    ]
