from rest_framework import serializers 
from .models import Feedback,GymRate,Rate,TrainerRate,Gym, Trainer,Branch
from .services import RateService
from django.db import transaction

class RateSerializer(serializers.ModelSerializer):
    GymRate = serializers.SerializerMethodField()
    TrainerRate = serializers.SerializerMethodField()
    class Meta:
        model = Rate
        fields = '__all__'
        
    def get_GymRate(self, obj):

        try:
            rate = GymRate.objects.get(rate=obj.pk,rate__is_deleted=False).gym.gym.name
        except GymRate.DoesNotExist:
            rate = None
        return rate
    
    def get_TrainerRate(self, obj):
        
        try:
            rate = TrainerRate.objects.get(rate=obj.pk,rate__is_deleted=False).trainer.employee.user.username
        except TrainerRate.DoesNotExist:
            rate = None
        return rate
    
    def update(self,instance,data):
        try:
            return RateService.update_ratings(instance,data['value'],data['client'])
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
class CreateRateSerializer(serializers.ModelSerializer):
    gym = serializers.IntegerField(write_only=True,allow_null=True)
    trainer = serializers.IntegerField(write_only=True,allow_null=True)
    
    class Meta:
        model = Rate
        fields = '__all__'
        
    def validate(self,data):
        check = bool(data['gym']) + bool(data['trainer']) + bool(data['is_app_rate'])
        if check != 1:
            raise serializers.ValidationError('please check on the entered rated values')
        return super().validate(data)
    
    def create(self,validated_data):
        try:
            with transaction.atomic():
                rate = RateService.rate(validated_data)
            return rate
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
class FeedbackSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Feedback
        fields = '__all__'
        
        
class GymRateSerializer(serializers.ModelSerializer):
    gym = serializers.SerializerMethodField()
    avg_rate = serializers.FloatField(source='gym.rate',read_only=True)
    rate_num = serializers.IntegerField(source='gym.number_of_rates',read_only=True)
    
    class Meta:
        model = GymRate
        fields = ['gym','avg_rate','rate_num']
    
    def get_gym(self,obj):
        branch = Branch.objects.get(pk=obj.gym.pk)
        return {
            'branch_address':f'{branch.address}-{branch.city}-{branch.street}',
            'name':branch.gym.name,
            'client':obj.rate.client.user.username,
            'client_rate_value': obj.rate.value
        }

class TrainerRateSerializer(serializers.ModelSerializer):
    trainer = serializers.SerializerMethodField()
    avg_rate = serializers.FloatField(source='trainer.rate',read_only=True)
    rate_num = serializers.IntegerField(source='trainer.number_of_rates',read_only=True)
    
    class Meta:
        model = TrainerRate
        fields = ['trainer','avg_rate','rate_num']
        
    def get_trainer(self,obj):
        trainer = Trainer.objects.get(pk=obj.trainer.pk)
        return{
            'name':trainer.employee.user.username,
            'ratings':trainer.rate,
            'ratings_num':trainer.number_of_rates,
            'client':obj.rate.client.user.username,
            'client_rate_value': obj.rate.value
        }