# Generated by Django 5.0.6 on 2024-07-19 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0013_employee_num_of_trainees'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='allow_public_posts_for_trainers',
            field=models.BooleanField(default=True),
        ),
    ]
