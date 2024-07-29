from rest_framework import serializers 
from .models import *

class PointsSerializer(serializers.ModelSerializer):
    activity = serializers.CharField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Points
        fields = ['user','activity','points']
        
        def validate_points(self,data):
            if data < 0:
                raise serializers.ValidationError('Points cannot be negative')
            return data
        