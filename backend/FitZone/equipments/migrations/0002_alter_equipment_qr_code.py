# Generated by Django 5.0.6 on 2024-07-10 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='qr_code',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
