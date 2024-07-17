# Generated by Django 5.0.6 on 2024-07-15 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_remove_category_image_path_branch_product_color_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplements',
            name='servings',
        ),
        migrations.AddField(
            model_name='supplements',
            name='caffeine',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='supplements',
            name='carbs',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='supplements',
            name='protein',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, max_length=100),
        ),
    ]
