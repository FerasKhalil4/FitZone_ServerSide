# Generated by Django 5.0.6 on 2024-09-18 18:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_message_chatroom'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='chatroom',
            name='unique_users',
        ),
        migrations.AddConstraint(
            model_name='chatroom',
            constraint=models.UniqueConstraint(condition=models.Q(('user_1__lt', models.F('user_2'))), fields=('user_1', 'user_2'), name='unique_chatroom_users'),
        ),
    ]
