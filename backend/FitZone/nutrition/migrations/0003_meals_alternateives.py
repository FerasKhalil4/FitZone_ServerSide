# Generated by Django 5.0.6 on 2024-08-05 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0002_nutritionplan_is_same'),
    ]

    operations = [
        migrations.AddField(
            model_name='meals',
            name='alternateives',
            field=models.JSONField(default=dict),
        ),
    ]
