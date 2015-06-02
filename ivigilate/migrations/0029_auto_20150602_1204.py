# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ivigilate.models


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0028_event_schedule_timezone_offset'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='authuser',
            managers=[
                ('objects', ivigilate.models.AuthUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='authuser',
            name='account',
            field=models.ForeignKey(to='ivigilate.Account', related_name='users', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='authuser',
            name='email',
            field=models.EmailField(error_messages={'unique': 'The given email address has already been registered.'}, max_length=254, unique=True, help_text='Required.', verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='authuser',
            name='groups',
            field=models.ManyToManyField(verbose_name='groups', related_name='user_set', to='auth.Group', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user', blank=True),
        ),
        migrations.AlterField(
            model_name='authuser',
            name='last_login',
            field=models.DateTimeField(blank=True, verbose_name='last login', null=True),
        ),
        migrations.AlterField(
            model_name='movable',
            name='account',
            field=models.ForeignKey(to='ivigilate.Account', related_name='movables'),
        ),
        migrations.AlterField(
            model_name='place',
            name='account',
            field=models.ForeignKey(to='ivigilate.Account', related_name='places'),
        ),
    ]
