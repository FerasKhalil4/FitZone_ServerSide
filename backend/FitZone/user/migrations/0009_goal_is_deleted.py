# Generated by Django 5.0.6 on 2024-07-31 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_goal_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
