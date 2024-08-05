# Generated by Django 5.0.6 on 2024-08-03 08:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_branch_products_branch_product_constraint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meals',
            name='product',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='meals', to='store.product'),
        ),
        migrations.AddConstraint(
            model_name='supplements',
            constraint=models.UniqueConstraint(fields=('product', 'weight', 'flavor'), name='product_weight_flavor'),
        ),
    ]
