# Generated by Django 5.0.6 on 2024-07-16 15:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0011_remove_gym_regestration_price'),
        ('store', '0012_alter_variants_flavor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variants',
            name='product',
        ),
        migrations.RemoveField(
            model_name='variants',
            name='supplement_category',
        ),
        migrations.CreateModel(
            name='Accessories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=50, null=True)),
                ('size', models.CharField(max_length=50, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accessory', to='store.product')),
            ],
        ),
        migrations.CreateModel(
            name='Branch_products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.PositiveBigIntegerField(blank=True)),
                ('product_type', models.CharField(blank=True, max_length=50)),
                ('amount', models.PositiveIntegerField(default=0)),
                ('is_available', models.BooleanField(default=True)),
                ('price', models.FloatField(default=0.0)),
                ('points_gained', models.IntegerField(default=0)),
                ('image_path', models.ImageField(null=True, upload_to='images/')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='gym.branch')),
            ],
        ),
        migrations.CreateModel(
            name='Meals',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protein', models.FloatField(default=0.0, null=True)),
                ('carbs', models.FloatField(default=0.0, null=True)),
                ('calories', models.FloatField(default=0.0, null=True)),
                ('fats', models.FloatField(default=0.0, null=True)),
                ('used_for', models.CharField(blank=True, max_length=50)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meals', to='store.product')),
            ],
        ),
        migrations.CreateModel(
            name='Supplements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protein', models.FloatField(default=0.0, null=True)),
                ('carbs', models.FloatField(default=0.0, null=True)),
                ('calories', models.FloatField(default=0.0, null=True)),
                ('caffeine', models.FloatField(default=0.0, null=True)),
                ('weight', models.FloatField(default=0.0, null=True)),
                ('falvor', models.CharField(blank=True, max_length=50)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplemetns', to='store.product')),
                ('supplement_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplemetns', to='store.supplements_category')),
            ],
        ),
        migrations.DeleteModel(
            name='Branch_product',
        ),
        migrations.DeleteModel(
            name='Variants',
        ),
    ]
