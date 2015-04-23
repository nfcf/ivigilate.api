# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0011_auto_20150330_2319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sighting',
            name='watcher_uid',
        ),
        migrations.AddField(
            model_name='sighting',
            name='place',
            field=models.ForeignKey(null=True, to='ivigilate.Place'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sighting',
            name='user',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
