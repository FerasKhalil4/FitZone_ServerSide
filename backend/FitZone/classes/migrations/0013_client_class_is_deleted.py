# Generated by Django 5.0.6 on 2024-09-07 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0012_client_class_offered_total_client_class_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='client_class',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
