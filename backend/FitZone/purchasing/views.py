from rest_framework import generics,status
from rest_framework. decorators import api_view 
from store.models import Product
from store.serializers import PublicStoreSerializer,PrivateStoreSerializer,ProductSerializer
from store.models import Branch_products,Supplements,Accessories,Meals
from rest_framework.response import Response
from .DataExamples import private_purchasing,public_purchasing
from .serializers import Private_Store_Purchase_Serializer, Public_Store_Purchase_Serializer,CLientPurchasingsSerializer,EditPurchaseSerializer,AddProductsToPurchase
from .models import Purchase
from django.core.cache import cache
from offers.models import Offer
from gym.models import Branch 
from offers.serializers import Price_offersStoreSerializer
from drf_spectacular.utils import extend_schema
from datetime import datetime
from django.db import transaction
from user.models import Client
from .services.delete_purchase_service import Delete_Purchase


def get_products(qs):
    data = {}
    for product in qs:
        print(product)
        if product.amount > 0 and product.is_available:
            if product.product_type == 'Supplement':
                supplement = Supplements.objects.filter(pk=product.product_id).first()
                if supplement is not None:
                    if supplement.product.pk not in data:
                        data[supplement.product.pk] = ProductSerializer(supplement.product).data
                    
                
            elif product.product_type == 'Accessory':
                accessory = Accessories.objects.filter(pk=product.product_id).first()
                if accessory is not None:
                    if accessory.product.pk not in data:
                        data[accessory.product.pk] = ProductSerializer(accessory.product).data
            
            elif product.product_type == 'Meal':
                meal = Meals.objects.filter(pk=product.product_id).first()
                if meal is not None:
                    if meal.product.pk not in data:
                        data[meal.product.pk] = ProductSerializer(meal.product).data
                    
    return data

class PublicStoreListAV(generics.ListAPIView):
    serializer_class = ProductSerializer
    @extend_schema(
        summary='get products for public store' 
    )
    def get_queryset(self):
        qs = Branch_products.objects.filter(branch__gym__allow_public_products=True,branch__has_store=True)
        data = get_products(qs)
        return data
        
    def get(self,request,*args, **kwargs):
        cache_key = 'public_store_products'
        data = cache.get(cache_key)
        if not data:
            now = datetime.now().date()
            offers_qs = Offer.objects.filter(price_offers__isnull=False,start_date__lte=now,end_date__gte=now,
                                             is_deleted=False,branch__gym__allow_public_products=True,
                                             price_offers__objects__fee__isnull=True)
            offer_data =[]
            for offer in offers_qs:
                
                for product in offer.price_offers.objects.values():
                    amount_product = Branch_products.objects.get(pk=product['product_id']).amount
                    if amount_product > 0 :
                        offer_data.append(Price_offersStoreSerializer(offer).data)
            products_data = self.get_queryset()
            data = {
                'products':products_data,
                'offers':offer_data
            }
            cache.set(cache_key,data,timeout=60*20) 
            
        return Response(data,status=status.HTTP_200_OK)  
public_store = PublicStoreListAV.as_view()


class Public_Product_DetailsRetrieveAV(generics.RetrieveAPIView):
    serializer_class = PublicStoreSerializer
    queryset = Product.objects.filter(is_deleted=False)
    
product_details = Public_Product_DetailsRetrieveAV.as_view()


class Private_Product_DetailsRetrieveAV(generics.RetrieveAPIView):
    serializer_class = PrivateStoreSerializer
    queryset = Product.objects.filter(is_deleted=False)
    
    def get(self,request,*args, **kwargs):
        try:
            instance = Product.objects.get(id=self.kwargs['pk'])
            serilaizer = self.get_serializer(instance,context={'branch':self.kwargs['branch_id']}).data
            return Response(serilaizer,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
private_product_details = Private_Product_DetailsRetrieveAV.as_view()

def filtering_data(data,filtering):
    products = data.get('products').get('products').get(filtering)
    offers = data.get('offers')
    data = {
    'products':products,
    'offers':offers
                }
    return data

class PrivateStoreLisAV(generics.ListAPIView):
    serializer_class = PrivateStoreSerializer
    
    def get_queryset(self):
        branch_id = self.kwargs.get('branch_id')
        qs = Branch_products.objects.filter(branch=branch_id,branch__has_store=True)
        data = get_products(qs)
        return data
    
    def get(self,request,*args, **kwargs):
        try:
            branch= Branch.objects.get(pk=kwargs['branch_id'])
            cache_key = f'private_store_products{branch.pk}'
            data = cache.get(cache_key)
            
            filtering = request.GET.get('product_type', None)
            
            if filtering is not None and data is not None: 
                data = filtering_data(data,filtering)
                return Response(data,status=status.HTTP_200_OK)
                
            if not data:
                now = datetime.now().date()
                offers_qs = Offer.objects.filter(price_offers__isnull=False,branch=kwargs['branch_id'],start_date__lte=now,end_date__gte=now,
                                                                is_deleted=False,price_offers__objects__fee__isnull=True)
                
                offer_data =[]
                for offer in offers_qs:
                    
                    for product in offer.price_offers.objects.values():
                        amount_product = Branch_products.objects.get(pk=product['product_id']).amount
                        if amount_product > 0 :
                            offer_data.append(Price_offersStoreSerializer(offer).data)
                            
                products_data = self.get_queryset()
                data = {
                    'products':products_data,
                    'offers':offer_data
                }
                cache.set(cache_key,data,timeout=60*20) 
                if filtering:   
                    data = filtering_data(data,filtering)
                       
            return Response(data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
private_store = PrivateStoreLisAV.as_view()

class PurchasePrivateStoreAV(generics.CreateAPIView):
    serializer_class = Private_Store_Purchase_Serializer
    queryset = Purchase.objects.all()
    
    @extend_schema(
        summary='purchasing from private store',
        examples=private_purchasing
    )
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                request.data['branch']=kwargs['branch_id']
                return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
purchase_private_store = PurchasePrivateStoreAV.as_view()

class PurchasePublicStoreAV(generics.CreateAPIView):
    serializer_class=Public_Store_Purchase_Serializer
    queryset = Purchase.objects.all()
    @extend_schema(
        summary='purchasing from private store',
        examples=public_purchasing
    )
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
purchase_public_store = PurchasePublicStoreAV.as_view()

class CLientPurchasingsListAV(generics.RetrieveAPIView):
    serializer_class = CLientPurchasingsSerializer
    
    def get_object(self):
        try:
            return Client.objects.get(user=self.request.user.pk)
        except Client.DoesNotExist:
            raise ValueError('Client does not exist')
    @extend_schema(
        summary='return the client purchases history',
    )
    def get(self,request,*args,**kwargs):
        return super().get(request,*args,**kwargs)

purchases = CLientPurchasingsListAV.as_view()

class CLientPurchasingsDetailsAV(generics.RetrieveDestroyAPIView):
    serializer_class = Public_Store_Purchase_Serializer 
    queryset = Purchase.objects.filter(is_deleted=False)
    
    @extend_schema(
        summary='return the client specific purchase details',
    )
    def get(self,request,*args,**kwargs):
        return super().get(request,*args,**kwargs)
    
    @extend_schema(
        summary='delete the client specific purchase ',
    )
    def delete(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                Delete_Purchase.delete_purchase(self.get_object())
                return Response({'success': 'purchase was successfully deleted'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

purchases_details = CLientPurchasingsDetailsAV.as_view()

class ProductsEditCheckAV(generics.RetrieveAPIView):   
    serializer_class = EditPurchaseSerializer
    queryset = Purchase.objects.all()
    
    @extend_schema(
        summary='check if the user can update his purchase',
        description = 'this will return the product the user can update'
    )
    def get(self, request, *args, **kwargs):
        check = self.get_serializer(self.get_object()).data
        if check['products']is not None:
            return Response(check,status=status.HTTP_200_OK)
        return Response({'error':'you cannot edit your purchases'},status=status.HTTP_400_BAD_REQUEST)

check_purchasings = ProductsEditCheckAV.as_view()



class UpdatePurchaseProductsDetailsAV(generics.UpdateAPIView):
    serializer_class = EditPurchaseSerializer
    queryset = Purchase.objects.all()
    
    @extend_schema(
        summary='update the client purchases',
        description='you may pass either the amount or the is_deleted field'
    )
    def put(self,request,*args,**kwargs):
        try:
            with transaction.atomic():
                return super().put(request,*args,**kwargs)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

update_purchase = UpdatePurchaseProductsDetailsAV.as_view()
    
class AddProductsToPurchaseAV(generics.CreateAPIView):
    serializer_class = AddProductsToPurchase
    queryset = Purchase.objects.all()
    
    @extend_schema(
        summary='add products to purchase',
        examples=[]
    )
    
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                request.data['purchase_id'] = kwargs.pop('pk')
                return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
add_products = AddProductsToPurchaseAV.as_view()
