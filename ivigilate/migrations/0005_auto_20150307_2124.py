# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0004_auto_20150307_1810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='name',
            field=models.CharField(blank=True, max_length=64),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='place',
            name='reference_id',
            field=models.CharField(blank=True, max_length=64),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='place',
            name='uid',
            field=models.CharField(max_length=36),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('account', 'uid')]),
        ),
    ]
