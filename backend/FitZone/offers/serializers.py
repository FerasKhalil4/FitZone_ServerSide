from django.db.models import Q
from rest_framework import serializers 
from .models import *
from gym.seriailizers import BranchSerializer
import datetime

class PercentageOfferSerializer(serializers.ModelSerializer):
    offer_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Percentage_offer
        fields = [ 'offer_id', 'percentage_cut', 'class_id', 'fee', 'category', 'supp_category']

class ObjectHasPriceOfferSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ObjectHasPriceOffer
        fields = ['id','fee','product','number']
        

        
class PriceOfferSerializer(serializers.ModelSerializer):
    offer_id = serializers.IntegerField(write_only=True)
    price_offer_objects = ObjectHasPriceOfferSerializer(source="objects",read_only=True,many=True)
    class Meta:
        model = Price_Offer
        fields = ['offer_id','price','price_offer_objects']
        


        
class OfferSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True,input_formats=["%Y-%m-%d"])
    end_date = serializers.DateField(required=True,input_formats=["%Y-%m-%d"])  
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(source ='branch',queryset = Branch.objects.all(),write_only=True)
    percentage_offer = PercentageOfferSerializer(source = "percentage_offers", read_only=True)
    price_offer = PriceOfferSerializer(source = "price_offers",read_only=True)
    class Meta:
        model = Offer
        fields = ['id','start_date','end_date','image_path','branch_id','branch','percentage_offer','price_offer']
        
        def validate(self,data):

            if data.get('start_date') > data.get('end_date'):
                raise serializers.ValidationError('Start date should be less than end date')
            current_date = datetime.datetime.now().date()
            if data.get('start_date') < current_date or data.get('end_date') < current_date:
                raise serializers.ValidationError('the start date and the end date must be more than the current date')
                
            return data