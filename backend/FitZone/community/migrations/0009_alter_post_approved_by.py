# Generated by Django 5.0.6 on 2024-07-09 16:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0008_alter_image_post_alter_video_post'),
        ('gym', '0008_gym_allow_public_posts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='approved_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approved', to='gym.employee'),
        ),
    ]
