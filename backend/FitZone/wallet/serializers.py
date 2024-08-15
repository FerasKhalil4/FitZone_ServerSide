from rest_framework import serializers
from .models import *
class WalletSerializer(serializers.ModelSerializer):
    wallet_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    class Meta:
        model = Wallet
        fields = ['wallet_id','balance','client']
        
    def validate_balance(self, balance):
        if balance < 0:
            raise serializers.ValidationError('Balance cannot be negative')
        return balance

class DepositSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Wallet_Deposit
        fields = ['id','employee','client','amount','transaction_type']
        
    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError('Amount must be greater than zero')
        return amount