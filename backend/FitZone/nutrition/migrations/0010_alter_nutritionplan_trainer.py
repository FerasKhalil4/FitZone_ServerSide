# Generated by Django 5.0.6 on 2024-09-07 18:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0027_gym_allowed_number_for_update'),
        ('nutrition', '0009_remove_nutritionplan_calories_required_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nutritionplan',
            name='trainer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nutrition_plans', to='gym.trainer'),
        ),
    ]
