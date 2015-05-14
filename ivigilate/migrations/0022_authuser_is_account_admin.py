# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0021_auto_20150510_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='authuser',
            name='is_account_admin',
            field=models.BooleanField(default=False, verbose_name='account admin status', help_text='Designates whether the user is account admin.'),
            preserve_default=True,
        ),
    ]
