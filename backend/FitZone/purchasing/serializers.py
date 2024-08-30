from rest_framework import serializers
from .models import *
from .services import PrivateStoreService,PublicPurchaseService
from store.serializers import Branch_productSerializer
from offers.serializers import OfferSerializer
from user.models import Client
from gym.models import Branch
from django.core.validators import MinValueValidator

class Purchase_Product_Serializer(serializers.ModelSerializer):
    purchase_product_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    product_details = Branch_productSerializer(source='product' ,read_only=True)
    class Meta:
        model = Purchase_Product
        fields = ['purchase_product_id','product','purchase','amount','product_details']
        
class Purchase_Price_Offer_Serializer(serializers.ModelSerializer):
    purchase_price_offer_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    offer_detail = OfferSerializer(source='price_offer.offer',read_only=True)
    class Meta:
        model = Purchase_PriceOffer
        fields = ['purchase_price_offer_id','price_offer','purchase','amount','offer_detail']
        
class Branch_Products_PurchaseSerilaizer(serializers.Serializer):
    
    amount = serializers.IntegerField(validators = [MinValueValidator(1)])
    branch_product_id = serializers.PrimaryKeyRelatedField(queryset=Branch_products.objects.filter(is_available=True))
    
        
class Price_Offers_PurchaseSerilaizer(serializers.Serializer):
    amount = serializers.IntegerField(validators = [MinValueValidator(1)])
    offer_id =serializers.IntegerField()

class Private_Store_Purchase_Serializer(serializers.ModelSerializer):
    product_purchased = Purchase_Product_Serializer(source='products',read_only=True,many=True)
    price_offers_purchased = Purchase_Price_Offer_Serializer(source='PriceOffers',many=True,read_only=True)
    purchase_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    offered_total = serializers.FloatField(read_only=True)
    total = serializers.FloatField(read_only=True)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.filter(is_active=True),write_only=True)
    products =Branch_Products_PurchaseSerilaizer(many=True,write_only=True)

    vouchers = serializers.ListField(
        child = serializers.CharField() 
        ,write_only=True
    )
    price_offers = Price_Offers_PurchaseSerilaizer(many=True,write_only=True)
    
    class Meta:
        model = Purchase
        fields = ['purchase_id','total','offered_total','created_at','products','vouchers','price_offers','branch','product_purchased','price_offers_purchased']
    
    def create(self, validated_data):
        validated_data['client'] = Client.objects.get(user=self.context.get('request').user.pk)
        purchase = PrivateStoreService.Purchase(validated_data)
        return purchase 
class PublicStoreProducts(Branch_Products_PurchaseSerilaizer):
    branch_id = serializers.PrimaryKeyRelatedField(queryset = Branch.objects.filter(is_active = True))

class PublicPriceOffersSerilaizer(Price_Offers_PurchaseSerilaizer):
    branch_id = serializers.PrimaryKeyRelatedField(queryset = Branch.objects.filter(is_active = True))

class Public_Store_Purchase_Serializer(serializers.ModelSerializer):
    product_purchased = Purchase_Product_Serializer(source='products',read_only=True,many=True)
    price_offers_purchased = Purchase_Price_Offer_Serializer(source='PriceOffers',many=True,read_only=True)
    purchase_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    offered_total = serializers.FloatField(read_only=True)
    total = serializers.FloatField(read_only=True)
    products = PublicStoreProducts(many=True,write_only=True)
    vouchers = serializers.ListField(
        child = serializers.CharField() 
        ,write_only=True
    )
    price_offers = PublicPriceOffersSerilaizer(many=True,write_only=True)
    
    
    class Meta:
        model = Purchase
        fields = ['products','purchase_id','offered_total','total','vouchers','price_offers','product_purchased','price_offers_purchased']
        
    def create(self, validated_data):
        validated_data['client'] = Client.objects.get(user=self.context.get('request').user.pk)
        purchase = PublicPurchaseService.Purchase(validated_data)
        return purchase