# Generated by Django 5.0.6 on 2024-08-19 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipments', '0021_equipment_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='category',
            field=models.CharField(choices=[('Cardio', 'Cardio'), ('Equipment', 'Equipment'), ('Free-Weights', 'Free-Weights')], max_length=20),
        ),
    ]
