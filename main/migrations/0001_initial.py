# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-28 02:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.CharField(default=main.models.generate_uuid, editable=False, max_length=30, primary_key=True, serialize=False)),
                ('sender_name', models.CharField(default=main.models.generate_fake_name, max_length=1000)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.CharField(default=main.models.generate_uuid, editable=False, max_length=30, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('direction', models.CharField(choices=[('F', 'Forwarded'), ('S', 'Sent'), ('R', 'Received')], max_length=10)),
                ('sender', models.CharField(blank=True, max_length=1000)),
                ('recipient', models.CharField(blank=True, max_length=1000)),
                ('subject', models.CharField(max_length=1000)),
                ('body', models.TextField()),
                ('stripped_body', models.TextField(blank=True)),
                ('stripped_signature', models.TextField(blank=True)),
                ('message_id', models.CharField(default=main.models.generate_message_id, max_length=1000, unique=True)),
                ('in_reply_to', models.CharField(blank=True, max_length=1000)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Conversation')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]