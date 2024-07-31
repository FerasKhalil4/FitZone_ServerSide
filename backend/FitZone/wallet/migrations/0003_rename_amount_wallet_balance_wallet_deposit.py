# Generated by Django 5.0.6 on 2024-07-29 09:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0018_trainer_online_trainine_price_and_more'),
        ('user', '0007_client_image_path'),
        ('wallet', '0002_alter_wallet_updated_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wallet',
            old_name='amount',
            new_name='balance',
        ),
        migrations.CreateModel(
            name='Wallet_Deposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='depositWallet', to='user.client')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='walletDeposit', to='gym.employee')),
            ],
        ),
    ]
