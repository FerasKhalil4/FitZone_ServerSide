from rest_framework import serializers
from .models import Wallet
class WalletSerializer(serializers.ModelSerializer):
    wallet_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    class Meta:
        model = Wallet
        fields = ['wallet_id','amount','client']