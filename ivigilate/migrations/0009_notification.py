# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0008_auto_20150621_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('metadata', models.TextField(blank=True)),
                ('occurred_at', models.DateTimeField(editable=False)),
                ('displayed_at', models.DateTimeField(editable=False)),
                ('cleared_at', models.DateTimeField(editable=False)),
                ('beacon', models.ForeignKey(to='ivigilate.Beacon')),
                ('event', models.ForeignKey(to='ivigilate.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
