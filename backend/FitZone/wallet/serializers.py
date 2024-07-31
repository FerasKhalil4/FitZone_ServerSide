from rest_framework import serializers
from .models import *
class WalletSerializer(serializers.ModelSerializer):
    wallet_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    class Meta:
        model = Wallet
        fields = ['wallet_id','balance','client']

class DepositSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Wallet_Deposit
        fields = ['id','employee','client','amount']