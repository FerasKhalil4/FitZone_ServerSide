from rest_framework import serializers
from .models import (Gym_Subscription, Branch_Sessions,Percentage_offer,
                     Registration_Fee,
                     ObjectHasPriceOffer,now)
from .services import OfferSubscriptionService
from gym.seriailizers import Registration_FeeSerializer


class Client_BranchSerializer(serializers.ModelSerializer):
    
    subscribtion_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    fee_data = Registration_FeeSerializer(source='registration_type',read_only=True)
    offer_code = serializers.CharField(write_only=True,allow_null=True)
    vouchers = serializers.ListField(write_only=True)
    class Meta:
        model = Gym_Subscription
        fields = ['subscribtion_id','client','branch','registration_type','start_date','end_date','is_active',
                  'fee_data','price_offer','offer_code','vouchers']
        read_only_fields = ['subscribtion_id','is_active','end_date','start_date']
        
    def create(self, data):
        data = OfferSubscriptionService.offer_check(data)
        instance = Gym_Subscription.objects.create(**data)
        return instance
    
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
        
        
    
    
        