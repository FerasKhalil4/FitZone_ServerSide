# Generated by Django 5.0.6 on 2024-09-22 15:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_sessions', '0007_alter_branch_sessions_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch_sessions',
            name='end_session',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 22, 18, 35, 58, 930251)),
        ),
    ]
