# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0016_auto_20151006_0826'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventoccurrence',
            name='beacon',
        ),
    ]
