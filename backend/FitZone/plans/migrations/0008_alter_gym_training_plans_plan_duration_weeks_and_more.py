# Generated by Django 5.0.6 on 2024-07-28 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0007_remove_workout_exercises_unique_order_workout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gym_training_plans',
            name='plan_duration_weeks',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='workout',
            name='cardio_duration',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='workout',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='workout_exercises',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='workout_exercises',
            name='sets',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
