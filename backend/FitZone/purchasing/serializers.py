from rest_framework import serializers
from .models import *
from .services import(private_store_service,public_store_services,update_service,OffersService)
from store.serializers import Branch_productSerializer
from offers.serializers import OfferSerializer
from user.models import Client
from gym.models import Branch
from django.core.validators import MinValueValidator
from django.db import transaction
class Purchase_Product_Serializer(serializers.ModelSerializer):
    purchase_product_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    product_details = Branch_productSerializer(source='product' ,read_only=True)
    class Meta:
        model = Purchase_Product
        fields = ['purchase_product_id','product','purchase_id','amount','product_details','product_total','product_offer_total']
        
class Purchase_Price_Offer_Serializer(serializers.ModelSerializer):
    purchase_price_offer_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    offer_detail = OfferSerializer(source='price_offer.offer',read_only=True)
    class Meta:
        model = Purchase_PriceOffer
        fields = ['purchase_price_offer_id','price_offer','purchase_id','amount','offer_detail','offer_total']
        
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
        user = self.context.get('request').user.pk
        validated_data['client'] = Client.objects.get(user=user)
        purchase = private_store_service.PrivateStoreService.Purchase(validated_data)
        return purchase 
    
    
class PublicStoreProducts(Branch_Products_PurchaseSerilaizer):
    branch_id = serializers.PrimaryKeyRelatedField(queryset = Branch.objects.filter(is_active = True),required=False)

class PublicPriceOffersSerilaizer(Price_Offers_PurchaseSerilaizer):
    branch_id = serializers.PrimaryKeyRelatedField(queryset = Branch.objects.filter(is_active = True),required=False)

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
        fields = ['products','purchase_id','created_at','offered_total','total','vouchers','price_offers','product_purchased','price_offers_purchased']
        
    def validate(self, data):
        product_branch_ids = [item['branch_id'] for item in data['products'] if 'branch_id' in item]
        offer_branch_ids = [item['branch_id'] for item in data['price_offers'] if 'branch_id' in item]
        if (len(offer_branch_ids) != len(data['price_offers'])) or(len(product_branch_ids) != len(data['products'])):
            raise serializers.ValidationError('please ensure passing the branch_ids to the price offers and the products')
        return super().validate(data)
        
    def create(self, validated_data):
        try:
            user = self.context.get('request').user.pk
            validated_data['client'] = Client.objects.get(user=user)
        except Client.DoesNotExist:
            print('client does not exist')
        print(validated_data)
        purchase = public_store_services.PublicPurchaseService.Purchase(validated_data)
        return purchase


class CLientPurchasingsSerializer(serializers.ModelSerializer):
    purhcsings = serializers.SerializerMethodField()
    class Meta:
        model = Client 
        fields = ['purhcsings']
        
    def get_purhcsings(self, obj):
        purchases = Purchase.objects.filter(client=obj,is_deleted=False)
        serializer = Public_Store_Purchase_Serializer(purchases, many=True)
        return serializer.data



def validate_fields(data):
    if ('amount' in data) and ('is_deleted' in data):
        raise serializers.ValidationError('please either update the amount or delete the product') 
    
class UpdateProductsSerialzier(serializers.Serializer):
    purchase_product_id = serializers.PrimaryKeyRelatedField(queryset=Purchase_Product.objects.filter(is_deleted=False))
    amount = serializers.IntegerField(validators = [MinValueValidator(1)],required=False)
    is_deleted = serializers.BooleanField(required=False)
    
    def validate(self, attrs):
        validate_fields(attrs)
        return super().validate(attrs)
    
class UpdateOfferSerialzier(serializers.Serializer):
    purchase_price_offer_id = serializers.PrimaryKeyRelatedField(queryset=Purchase_PriceOffer.objects.filter(is_deleted=False))
    amount = serializers.IntegerField(validators = [MinValueValidator(1)],required=False)
    is_deleted = serializers.BooleanField(required=False)
    
    def validate(self, attrs):
        validate_fields(attrs)
        return super().validate(attrs)

class EditPurchasesSerializer(serializers.ModelSerializer):
    products = Purchase_Product_Serializer(many=True,read_only=True)
    PriceOffers = Purchase_Price_Offer_Serializer(many=True,read_only=True)

    class Meta:
        model = Purchase 
        fields = ['products','PriceOffers']
            
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            # You can perform any additional modifications to the representation here
            representation['purchase_pk'] = instance.pk
            representation['purchase_from_public_store'] = instance.is_public
            representation['number_of_updates'] = instance.number_of_updates
            
            update_service.Check_Update.check_editings(representation)
            
            return representation
        except Exception as e:
            raise serializers.ValidationError(str(e))

    
    # def get_products(self, obj):
    #     items = update_service.Check_Update.check_editings(obj.pk)
    #     print('--------------------------------')
    #     if items is not None:
    #         return {
    #             'purchase_pk': obj.pk,
    #             'purchased_from_public_store': obj.is_public,
    #             'number_of_updates': obj.number_of_updates,
    #             'purchases': Purchase_Product_Serializer(items['purchases'], many=True).data,
    #             'offers': Purchase_Price_Offer_Serializer(items['offers'], many=True).data
    #         }
    #     else:
    #         return {"error": "'products' not found"}
        
class EditPurchaseSerializer(serializers.ModelSerializer):
    
    product_purchased = Purchase_Product_Serializer(source='products',read_only=True,many=True)
    price_offers_purchased = Purchase_Price_Offer_Serializer(source='PriceOffers',many=True,read_only=True)
    purchase_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    offered_total = serializers.FloatField(read_only=True)
    total = serializers.FloatField(read_only=True) 
    products_updated = UpdateProductsSerialzier(many=True,write_only=True)
    offers_updated = UpdateOfferSerialzier(many=True,write_only=True)
    
    class Meta:
        model = Purchase 
        fields = ['products_updated','offers_updated','purchase_id','number_of_updates','total',
                  'offered_total','offered_total','total','price_offers_purchased','product_purchased']
    
    def update(self,instance,validated_data):
        try:
            with transaction.atomic():
                instance = update_service.UpdatePurchasing.update_purchasing_instance(instance,validated_data)
                return instance
        except Exception as e:
            raise serializers.ValidationError(str(e)) 
    

        
        
class AddProductsToPurchase(serializers.ModelSerializer):
    
    product_purchased = Purchase_Product_Serializer(source='products',read_only=True,many=True)
    price_offers_purchased = Purchase_Price_Offer_Serializer(source='PriceOffers',many=True,read_only=True)
    purchase_id = serializers.PrimaryKeyRelatedField(source='id',queryset=Purchase.objects.filter(is_deleted=False))
    offered_total = serializers.FloatField(read_only=True)
    total = serializers.FloatField(read_only=True)
    products = PublicStoreProducts(many=True,write_only=True)
    vouchers = serializers.ListField(
        child = serializers.CharField() 
        ,write_only=True
    )
    price_offers = PublicPriceOffersSerilaizer(many=True,write_only=True)
    number_of_updates = serializers.IntegerField(required=True,allow_null=True)
    branch_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.filter(is_active=True),required=False)
    class Meta:
        model = Purchase
        fields = ['products','purchase_id','created_at','offered_total','total','vouchers','price_offers'
                  ,'product_purchased','price_offers_purchased','number_of_updates','branch_id']
        
    
    def create (self,data):
        try:
            with transaction.atomic():
                instance = update_service.AddProductToPurchase.add_product(data)
                return instance
        except Exception as e:
            raise serializers.ValidationError(str(e)) 
        
class PurchaseSerializer(serializers.ModelSerializer):
    purchase_id = serializers.PrimaryKeyRelatedField(source='pk',read_only=True)
    class Meta:
        model = Purchase
        fields = ['purchase_id','total','offered_total','created_at','is_public','number_of_updates']
        
        
class PriceOffersStoreSerializer(serializers.ModelSerializer):
    price_offers_products = serializers.SerializerMethodField()
    price_offer_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields=['price_offer_details','price_offers_products']
    
    def get_price_offers_products(self,obj):
        try:
            
            data = OffersService.OfferService.retrieve_offer_products(obj)
            return data
        
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    def get_price_offer_details(self, obj):
        offer_data = OfferSerializer(obj).data
        offer_data['branch'] = offer_data['branch']['id']
        offer_data['price'] = offer_data['price_offer']['price']
        offer_data.pop('price_offer')
        offer_data.pop('percentage_offer')
        # offer_data.pop('price_offer_objects')
        return offer_data
        