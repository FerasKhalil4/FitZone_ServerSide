from rest_framework import serializers 
from .models import *
from .services import BlockService
from user.serializers import UserSerializer

class BlockSerializer(serializers.ModelSerializer):
    blocked_user_details = UserSerializer(source='blocked',read_only=True)
    class Meta:
        model = BlockList
        fields = '__all__'
        
    def create(self, validated_data):
        instance = BlockService.create_block(validated_data)
        return instance
    