# Generated by Django 5.0.6 on 2024-08-01 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0010_client_trianing_plan_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client_trianing_plan',
            name='end_date',
            field=models.DateField(null=True),
        ),
    ]
