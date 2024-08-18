# Generated by Django 5.0.6 on 2024-08-17 08:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0026_remove_gym_current_number_of_clients_and_more'),
        ('trainer', '0011_remove_client_trainer_client_trainer_registration_status_and_more'),
        ('user', '0014_goal_activity_level_goal_calories_required_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='client_trainer',
            name='client_trainer_registration_status',
        ),
        migrations.AddConstraint(
            model_name='client_trainer',
            constraint=models.UniqueConstraint(condition=models.Q(('end_date__gte', datetime.date(2024, 8, 17)), ('start_date__lte', datetime.date(2024, 8, 17))), fields=('client', 'trainer'), name='client_trainer_registration_status'),
        ),
    ]
