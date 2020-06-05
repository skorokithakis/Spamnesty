# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-11-21 14:43
from __future__ import unicode_literals

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("main", "0015_conversation_created")]

    operations = [
        migrations.AddIndex(
            model_name="message",
            index=models.Index(
                fields=["timestamp", "conversation", "direction"],
                name="main_messag_timesta_15e05b_idx",
            ),
        )
    ]
