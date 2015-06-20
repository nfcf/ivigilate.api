# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ivigilate', '0005_authuser_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Detector',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('uid', models.CharField(max_length=36)),
                ('reference_id', models.CharField(blank=True, max_length=64)),
                ('type', models.CharField(choices=[('M', 'Movable'), ('F', 'Fixed')], max_length=1, default='F')),
                ('name', models.CharField(blank=True, max_length=64)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('arrival_rssi', models.IntegerField(default=-85)),
                ('departure_rssi', models.IntegerField(default=-95)),
                ('metadata', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(related_name='detectors', to='ivigilate.Account')),
                ('updated_by', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='place',
            name='account',
        ),
        migrations.RemoveField(
            model_name='place',
            name='updated_by',
        ),
        migrations.AlterUniqueTogether(
            name='detector',
            unique_together=set([('account', 'uid', 'reference_id')]),
        ),
        migrations.RemoveField(
            model_name='event',
            name='places',
        ),
        migrations.RemoveField(
            model_name='sighting',
            name='place',
        ),
        migrations.DeleteModel(
            name='Place',
        ),
        migrations.AddField(
            model_name='event',
            name='detectors',
            field=models.ManyToManyField(blank=True, to='ivigilate.Detector'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sighting',
            name='detector',
            field=models.ForeignKey(null=True, to='ivigilate.Detector'),
            preserve_default=True,
        ),
    ]
