# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0010_auto_20151003_1129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='beacon',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='event',
        ),
    ]
