from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client
from datetime import date

class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(max_length=100, write_only=True)
    age = serializers.SerializerMethodField(read_only=True)
    birth_date = serializers.DateField(input_formats=["%Y-%m-%d"] , required = True)
    class Meta:
        model = User
        fields = [
            'id',
            'username', 
            'password', 
            'password2',
            'email',
            'gender',
            'birth_date',
            'role',
            'age',
        ]
        
        
    def get_age(self , instance):
        birth_date = instance.birth_date
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
        
    def validate(self, data):
        password1 = data.get('password')
        password2 = data.get('password2')
        if password1 != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        return data

    
    def validate_birth_date(self,birth_date):
        if birth_date is not None:
            today = date.today()
            age = today.year - birth_date.year - ((today.month , today.day) < (birth_date.month , birth_date.day))
            if age < 15 :
                raise serializers.ValidationError({'error':'age must be more or equal for 15'})
            return birth_date
        else :
            raise serializers.ValidationError({'error':'please check on the birth_Data'})
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('password2',None)
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
        
        
    
class ClientSerializer(serializers.ModelSerializer):
    points = serializers.IntegerField(read_only=True)
    user_profile = UserSerializer(write_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id',
            'user',
            'user_profile',
            'wakeup_time',
            'address',
            'height',
            'points',
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user_profile', None)
        user_data['role'] = 5
        if user_data is not None:
            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid(raise_exception=True):               
                user = user_serializer.save()
            else:
                raise serializers.ValidationError({'error': user_serializer.errors})
        else:
            raise serializers.ValidationError({'error': 'no such user'})
        
        client = Client.objects.create(user=user, **validated_data)
        return client
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user_profile', None)
        if user_data:
            user = instance.user
            user_serializer = UserSerializer(user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance