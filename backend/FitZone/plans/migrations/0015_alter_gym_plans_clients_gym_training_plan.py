# Generated by Django 5.0.6 on 2024-08-15 20:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0014_alter_workout_has_cardio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gym_plans_clients',
            name='gym_training_plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='plans.gym_training_plans'),
        ),
    ]
