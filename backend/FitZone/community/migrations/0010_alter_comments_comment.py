# Generated by Django 5.0.6 on 2024-07-11 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0009_alter_post_approved_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='comment',
            field=models.TextField(blank=True),
        ),
    ]
