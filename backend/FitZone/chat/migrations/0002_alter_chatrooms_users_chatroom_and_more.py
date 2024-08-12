# Generated by Django 5.0.6 on 2024-08-12 16:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatrooms_users',
            name='chatroom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='chat.chatroom'),
        ),
        migrations.AlterField(
            model_name='chatrooms_users',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chatrooms', to=settings.AUTH_USER_MODEL),
        ),
    ]
