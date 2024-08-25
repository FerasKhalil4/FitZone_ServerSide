from rest_framework import serializers
from .models import (Gym_Subscription, Branch_Sessions)
from .services import OfferSubscriptionService,Activate_Gym_Training_PlanService
from gym.seriailizers import Registration_FeeSerializer
from equipments.serializers import DiagramSerialzier

class Client_BranchSerializer(serializers.ModelSerializer):
    
    subscribtion_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    fee_data = Registration_FeeSerializer(source='registration_type',read_only=True)
    offer_code = serializers.CharField(write_only=True,allow_null=True)
    vouchers = serializers.ListField(write_only=True)
    activate_gym_plan = serializers.BooleanField(write_only=True)
    class Meta:
        model = Gym_Subscription
        fields = ['subscribtion_id','client','branch','registration_type','start_date','end_date',
                  'is_active','activate_gym_plan',
                  'fee_data','price_offer','offer_code','vouchers']
        read_only_fields = ['subscribtion_id','is_active','end_date','start_date']
        
    def create(self, data):
        data = OfferSubscriptionService.offer_check(data)
        check_plan_activation = data.pop('activate_gym_plan',None)
        if check_plan_activation :
            Activate_Gym_Training_PlanService.add_training_plan(data)
        print('check')
        
        return Gym_Subscription.objects.create(**data)
    
    def update(self,instance,data):

        data = OfferSubscriptionService.offer_check(data)
        return super().update(instance,data)
        

        
class Branch_SessionsSerializer(serializers.ModelSerializer):
    session_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    start_date = serializers.DateField(source ='sessions.gym_sessions.start_date',read_only=True) 
    end_date = serializers.DateField(source ='sessions.gym_sessions.end_date',read_only=True)    
    
    class Meta: 
        model = Branch_Sessions
        fields = ['session_id','client','branch','created_at','start_date','end_date']
        