# Generated by Django 5.0.6 on 2024-07-15 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_supplements_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplements',
            name='calories',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='supplements',
            name='flavour',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
