# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-19 12:13
from __future__ import unicode_literals

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("main", "0013_auto_20161124_2354")]

    operations = [
        migrations.AddField(
            model_name="message",
            name="forwarder",
            field=models.CharField(blank=True, max_length=1000),
        )
    ]
