# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0004_auto_20150618_1824'),
    ]

    operations = [
        migrations.AddField(
            model_name='authuser',
            name='photo',
            field=models.FileField(null=True, blank=True, upload_to='photos'),
            preserve_default=True,
        ),
    ]
