# Generated by Django 5.0.6 on 2024-08-05 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0003_meals_alternateives'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealsschedule',
            name='same_as_day',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
