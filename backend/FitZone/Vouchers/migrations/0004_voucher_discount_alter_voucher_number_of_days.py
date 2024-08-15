# Generated by Django 5.0.6 on 2024-08-15 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Vouchers', '0003_redeem_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='voucher',
            name='discount',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='voucher',
            name='number_of_days',
            field=models.IntegerField(),
        ),
    ]
