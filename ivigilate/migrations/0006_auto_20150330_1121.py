# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0005_auto_20150328_1725'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventaction',
            name='event',
        ),
        migrations.DeleteModel(
            name='EventAction',
        ),
        migrations.RemoveField(
            model_name='eventtrigger',
            name='event',
        ),
        migrations.RemoveField(
            model_name='eventtrigger',
            name='movable',
        ),
        migrations.DeleteModel(
            name='EventTrigger',
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='group_id',
            new_name='class_id',
        ),
        migrations.RemoveField(
            model_name='eventlimit',
            name='occurrence_count',
        ),
        migrations.RemoveField(
            model_name='eventoccurrence',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='eventoccurrence',
            name='places',
        ),
        migrations.RemoveField(
            model_name='movable',
            name='event_limits',
        ),
        migrations.RemoveField(
            model_name='movable',
            name='event_occurrences',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='events',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='sightings',
        ),
        migrations.AddField(
            model_name='event',
            name='movables',
            field=models.ManyToManyField(to='ivigilate.Movable', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='places',
            field=models.ManyToManyField(to='ivigilate.Place', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventoccurrence',
            name='duration_in_seconds',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventoccurrence',
            name='schedule',
            field=models.ForeignKey(to='ivigilate.Schedule', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventoccurrence',
            name='sightings',
            field=models.ManyToManyField(to='ivigilate.Sighting'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='authuser',
            name='is_staff',
            field=models.BooleanField(default=False, verbose_name='staff status', help_text='Designates whether the user can log into the admin site.'),
            preserve_default=True,
        ),
    ]
