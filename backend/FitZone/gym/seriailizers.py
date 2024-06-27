from rest_framework import serializers

from .models import Gym

class GymSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Gym
        exclude =['created_at']
        