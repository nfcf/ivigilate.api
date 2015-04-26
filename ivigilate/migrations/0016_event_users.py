# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0015_auto_20150426_0947'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
