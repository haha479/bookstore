# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-04 07:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Passport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_delete', models.BooleanField(default=False, verbose_name=b'\xe5\x88\xa0\xe9\x99\xa4\xe6\xa0\x87\xe8\xae\xb0')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('updata_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('username', models.CharField(max_length=20, verbose_name='\u7528\u6237\u540d')),
                ('password', models.CharField(max_length=40, verbose_name='\u5bc6\u7801')),
                ('email', models.EmailField(max_length=254, verbose_name='\u7528\u6237\u90ae\u7bb1')),
                ('is_active', models.BooleanField(default=False, verbose_name='\u6fc0\u6d3b\u72b6\u6001')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
