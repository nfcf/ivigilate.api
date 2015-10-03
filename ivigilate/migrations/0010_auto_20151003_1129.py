# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0009_notification'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='occurred_at',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='cleared_at',
            new_name='updated_at',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='displayed_at',
        ),
        migrations.AddField(
            model_name='notification',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='updated_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
