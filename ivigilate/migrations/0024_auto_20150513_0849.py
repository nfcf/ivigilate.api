# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0023_auto_20150513_0847'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authuser',
            name='is_account_owner',
        ),
        migrations.AddField(
            model_name='authuser',
            name='is_account_admin',
            field=models.BooleanField(help_text='Designates whether the user is as account admin.', verbose_name='account admin status', default=False),
            preserve_default=True,
        ),
    ]
