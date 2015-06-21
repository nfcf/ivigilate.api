# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0007_authuser_reference_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authuser',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='authuser',
            name='reference_id',
        ),
        migrations.RemoveField(
            model_name='event',
            name='users',
        ),
        migrations.RemoveField(
            model_name='sighting',
            name='user',
        ),
        migrations.AddField(
            model_name='detector',
            name='photo',
            field=models.FileField(blank=True, null=True, upload_to='photos'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='detector',
            name='type',
            field=models.CharField(default='F', choices=[('M', 'Movable'), ('F', 'Fixed'), ('U', 'User')], max_length=1),
            preserve_default=True,
        ),
    ]
