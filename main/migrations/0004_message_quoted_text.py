# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-01 06:48
from __future__ import unicode_literals

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("main", "0003_remove_message_stripped_signature")]

    operations = [
        migrations.AddField(
            model_name="message", name="quoted_text", field=models.TextField(blank=True)
        )
    ]
