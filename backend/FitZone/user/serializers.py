from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client, Goal
from datetime import date
from wallet.serializers import WalletSerializer
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.db.models import Q
import datetime

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
    predicted_date = serializers.DateField(required=True,input_formats=["%Y-%m-%d"])
    is_deleted = serializers.BooleanField(write_only=True,required=False)
    class Meta:
        model = Goal
        fields = ['client','weight','goal','goal_weight','predicted_date','status','is_deleted','number_updates','achieved_weight']
        ordering = ['created_at']
        read_only_fields = ['number_updates','status']

    def validate(self, data):
        today = date.today()
        client = self.context.get('client')
        check = Goal.objects.filter(predicted_date__gt = today , client=client)
        if check.exists():
            raise serializers.ValidationError("A future prediction already exists. Please resolve it before creating a new one.")
        if 'predicted_date' in data : 
            if data['predicted_date'] < today:
                raise serializers.ValidationError('The date must be in the future')
        if 'goal' in data: 
            if data['goal'] not in ['Lose Weight','Maintain Weight','Gain Weight']:
                raise serializers.ValidationError('please provide valid goal : Lose Weight, Maintain Weight, Gain Weight')
        return data
    
    def update(self, instance ,data):
        try:
            today = date.today()
            if instance.predicted_date > today:
                if instance.number_updates == 0 :
                    raise serializers.ValidationError('you cant update the goal any more please stay discipline and consistent to achieve your goal')
                data.pop('achieved_weight')
                for attr, value in data.items():
                    setattr(instance, attr, value)
                instance.number_updates -= 1
                instance.save()
                return instance
            else : 
                if instance.achieved_weight is None:
                    if 'achieved_weight' in data :
                        if (data['achieved_weight'] >= instance.goal_weight  and instance.goal == 'Gain Weight')or \
                        data['achieved_weight'] <= instance.goal_weight  and instance.goal == 'Lose Weight' :
                            status = 'Achieved' 
                        else:
                            status = 'Missed'
                        instance.achieved_weight = data['achieved_weight']
                        instance.status = status
                        instance.save()
                        return instance
                    else : 
                        raise serializers.ValidationError('you cant update but the status and the achieved weight')

                else:
                    raise serializers.ValidationError('you cant update this goal')
        except Exception as e :
            raise serializers.ValidationError(str(e))
        
class ClientSerializer(serializers.ModelSerializer):
    points = serializers.IntegerField(read_only=True)
    user_profile = UserSerializer(write_only=True)
    history = GoalSerializer(read_only=True,many=True)
    user = UserSerializer(read_only=True)
    current_BMI = serializers.SerializerMethodField()
    wallet = WalletSerializer(read_only=True)
    current_weight = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id',
            'user',
            'user_profile',
            'address',
            'height',
            'points',
            'history',
            'current_BMI',
            'wallet',
            'image_path',
            'current_weight',
        ]
    
    def get_current_BMI(self, obj):
        try:
            height = obj.height / 100
            goal = Goal.objects.get(client_id=obj.pk,status='Active')
            print(goal)
            if goal is not None :
                weight = goal.weight
            return weight / height ** 2
        except Goal.DoesNotExist:
            raise serializers.ValidationError({'error':'please provide weight'})
    
    def get_current_weight(self,obj):
        weight = Goal.objects.get(client=obj.pk,status='Active').weight
        return weight
    def create(self, validated_data):
        user_data = validated_data.pop('user_profile', None)
        request = self.context.get('request')
        base_url = get_current_site(request)
        
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
        url = f"http://{base_url}{reverse('employeeClientCheck', args=[str(client.pk)])}"
        client.url = url
        client.save()
        
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


        