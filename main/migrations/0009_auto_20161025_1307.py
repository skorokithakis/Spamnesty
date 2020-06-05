# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-25 13:07
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations
from django.db import models

import main.models


class Migration(migrations.Migration):

    dependencies = [("main", "0008_spamcategory")]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="category",
            field=models.ForeignKey(
                default=main.models.get_default_category,
                on_delete=django.db.models.deletion.CASCADE,
                to="main.SpamCategory",
            ),
        ),
        migrations.AddField(
            model_name="replytemplate",
            name="category",
            field=models.ForeignKey(
                default=main.models.get_default_category,
                on_delete=django.db.models.deletion.CASCADE,
                to="main.SpamCategory",
            ),
        ),
    ]
