# Generated by Django 5.0.6 on 2024-07-09 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0007_alter_shifts_shift_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='gym',
            name='allow_public_posts',
            field=models.BooleanField(default=True),
        ),
    ]
