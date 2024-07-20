# Generated by Django 5.0.6 on 2024-07-13 11:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0009_gym_allow_public_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='city',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='branch',
            name='street',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.CreateModel(
            name='Registration_Fee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
                ('fee', models.FloatField(default=0.0)),
                ('gym', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fees', to='gym.gym')),
            ],
        ),
    ]
