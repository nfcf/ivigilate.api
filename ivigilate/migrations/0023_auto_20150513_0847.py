# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0022_authuser_is_account_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authuser',
            name='is_account_admin',
        ),
        migrations.AddField(
            model_name='authuser',
            name='is_account_owner',
            field=models.BooleanField(verbose_name='account owner status', help_text='Designates whether the user is an account owner.', default=False),
            preserve_default=True,
        ),
    ]
