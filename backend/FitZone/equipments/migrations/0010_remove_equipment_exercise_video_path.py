# Generated by Django 5.0.6 on 2024-07-12 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('equipments', '0009_alter_equipment_exercise_video_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipment_exercise',
            name='video_path',
        ),
    ]
