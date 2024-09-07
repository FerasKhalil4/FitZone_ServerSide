# Generated by Django 5.0.6 on 2024-09-05 14:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0027_gym_allowed_number_for_update'),
        ('trainer', '0018_remove_client_trainer_client_trainer_registration_status_and_more'),
        ('user', '0014_goal_activity_level_goal_calories_required_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='client_trainer',
            name='client_trainer_registration_status',
        ),
        migrations.AddField(
            model_name='client_trainer',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name='client_trainer',
            constraint=models.UniqueConstraint(condition=models.Q(('end_date__gte', datetime.date(2024, 9, 5)), ('start_date__lte', datetime.date(2024, 9, 5)), models.Q(('registration_status', 'accepted'), ('registration_status', 'pending'), _connector='OR')), fields=('client',), name='client_trainer_registration_status'),
        ),
    ]
