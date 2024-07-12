from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client, Goal
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
            
        
class GoalSerializer(serializers.ModelSerializer):
    client = serializers.IntegerField(write_only=True)
    predicted_date = serializers.DateField(required=True,input_formats=["%Y-%m-%d"])
    class Meta:
        model = Goal
        fields = ['client','weight','goal','goal_weight','predicted_date']
        ordering = ['created_at']
    
    def validate(self, data):
        today = date.today()
        client = self.context.get('client')
        check = Goal.objects.filter(predicted_date__gt = today , client=client)
        if check.exists():
            raise serializers.ValidationError("A future prediction already exists. Please resolve it before creating a new one.")
        return data
        
class ClientSerializer(serializers.ModelSerializer):
    points = serializers.IntegerField(read_only=True)
    user_profile = UserSerializer(write_only=True)
    history = GoalSerializer(read_only=True,many=True)
    user = UserSerializer(read_only=True)
    current_BMI = serializers.SerializerMethodField()
    
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
            'history',
        ]
    
    def get_current_BMI(self, obj):
        height = obj.height
        weight = Goal.objects.get(predicted_date__gt=date.today()).weight
        return weight / pow(height,2)
    
    def create(self, validated_data):
        user_data = validated_data.pop('user_profile', None)
        try:
            user_data['role'] = 5
            if user_data is not None:
                user_serializer = UserSerializer(data=user_data)
                if user_serializer.is_valid(raise_exception=True):               
                    user = user_serializer.save()
                else:
                    raise serializers.ValidationError({'error': user_serializer.errors})
            else:
                raise serializers.ValidationError({'error': 'no data found'})
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        client = Client.objects.create(user=user, **validated_data)
        print(user)
        return {"client" : client , "user" : user}
    
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


        