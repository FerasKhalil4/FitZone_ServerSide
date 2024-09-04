from rest_framework import serializers
from .models import *
class WalletSerializer(serializers.ModelSerializer):
    wallet_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    client_data =serializers.SerializerMethodField()
    class Meta:
        model = Wallet
        fields = ['wallet_id','balance','client','client_data']
    
    def get_client_data(self,obj):
        client = obj.client
        return {
            'username':client.user.username,
            'name':f'{client.user.first_name} {client.user.last_name}',
            'email':client.user.email,
            'address':client.address,
        }
        
    def validate_balance(self, balance):
        if balance < 0:
            raise serializers.ValidationError('Balance cannot be negative')
        return balance

class DepositSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Wallet_Deposit
        fields = ['id','employee','client','amount','tranasaction_type']
        
    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError('Amount must be greater than zero')
        return amount