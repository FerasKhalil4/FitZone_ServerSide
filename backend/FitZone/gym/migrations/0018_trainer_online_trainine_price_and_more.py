# Generated by Django 5.0.6 on 2024-07-27 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0017_trainer_session_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainer',
            name='online_trainine_price',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='trainer',
            name='private_training_price',
            field=models.FloatField(default=0.0),
        ),
    ]
