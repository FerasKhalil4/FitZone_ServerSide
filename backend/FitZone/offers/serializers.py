from django.db.models import Q
from rest_framework import serializers 
from .models import *
from gym.seriailizers import BranchSerializer, Registration_FeeSerializer
from store.serializers import CategorySerializer, Supplements_CategorySerilaizer,Branch_productSerializer
from classes.serializers import Class_ScheduelSerializer
import datetime

class PercentageOfferSerializer(serializers.ModelSerializer):
    offer_id = serializers.PrimaryKeyRelatedField(source="offer.pk",queryset = Offer.objects.all(),write_only=True)
    class_data = Class_ScheduelSerializer(source='class_id',read_only=True)
    fee_data = Registration_FeeSerializer(source ='fee',read_only=True)
    category_data = CategorySerializer(source ='category',read_only=True)
    supp_category_data = Supplements_CategorySerilaizer(source='supp_category',read_only=True)
     
    class Meta:
        model = Percentage_offer
        fields = [ 'offer_id', 'percentage_cut', 'class_id', 'fee', 'category', 'supp_category','class_data','fee_data','category_data','supp_category_data']

class ObjectHasPriceOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectHasPriceOffer
        fields = ['id', 'fee', 'product', 'number', 'offer']
        
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
    offer_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    class Meta:
        model = Offer
        fields = ['offer_id','start_date','end_date','branch_id','branch','percentage_offer','price_offer']
        
        def validate(self,data):

            if data.get('start_date') > data.get('end_date'):
                raise serializers.ValidationError('Start date should be less than end date')
            current_date = datetime.datetime.now().date()
            if data.get('start_date') < current_date or data.get('end_date') < current_date:
                raise serializers.ValidationError('the start date and the end date must be more than the current date')
                
            return data