# Generated by Django 5.0.6 on 2024-09-08 22:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('community', '0012_rename_like_count_post_reaction_count'),
        ('user', '0014_goal_activity_level_goal_calories_required_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Saved_Posts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='SavedPosts', to='user.client')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='SavedPosts', to='community.post')),
            ],
        ),
    ]
