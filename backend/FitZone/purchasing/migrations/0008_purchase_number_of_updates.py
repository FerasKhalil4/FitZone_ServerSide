# Generated by Django 5.0.6 on 2024-08-31 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0007_purchase_priceoffer_is_deleted_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='number_of_updates',
            field=models.IntegerField(default=0),
        ),
    ]
