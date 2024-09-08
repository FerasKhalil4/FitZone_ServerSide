# Generated by Django 5.0.6 on 2024-09-08 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0010_alter_nutritionplan_trainer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meals',
            name='portion_size',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='meals',
            name='portion_unit',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
