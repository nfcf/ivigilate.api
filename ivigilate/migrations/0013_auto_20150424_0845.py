# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0012_auto_20150421_2149'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='account',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='movables',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='places',
        ),
        migrations.RemoveField(
            model_name='eventoccurrence',
            name='duration_in_seconds',
        ),
        migrations.RemoveField(
            model_name='eventoccurrence',
            name='schedule',
        ),
        migrations.DeleteModel(
            name='Schedule',
        ),
        migrations.RemoveField(
            model_name='eventoccurrence',
            name='sightings',
        ),
        migrations.AddField(
            model_name='event',
            name='schedule_days_of_week',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='schedule_end_time',
            field=models.TimeField(default='23:59:59'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='schedule_start_time',
            field=models.TimeField(default='00:00:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='sighting_is_confirmed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventlimit',
            name='metadata',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventlimit',
            name='updated_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventoccurrence',
            name='sighting',
            field=models.ForeignKey(to='ivigilate.Sighting', default=68),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='movable',
            name='uid',
            field=models.CharField(max_length=36),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='movable',
            unique_together=set([('account', 'uid', 'reference_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('account', 'uid', 'reference_id')]),
        ),
    ]
