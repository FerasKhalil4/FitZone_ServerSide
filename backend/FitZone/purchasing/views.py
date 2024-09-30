from rest_framework import generics,status
from store.models import Product
from store.serializers import PublicStoreSerializer,PrivateStoreSerializer,ProductSerializer
from store.models import Branch_products,Supplements,Accessories,Meals
from rest_framework.response import Response
from .DataExamples import private_purchasing,public_purchasing
from .serializers import (Private_Store_Purchase_Serializer, Public_Store_Purchase_Serializer,PurchaseSerializer
                            ,EditPurchaseSerializer,AddProductsToPurchase,EditPurchasesSerializer,PriceOffersStoreSerializer)
from store.serializers import Branch_productSerializer
from .models import Purchase
from offers.models import Offer
from offers.serializers import Price_offersStoreSerializer
from drf_spectacular.utils import extend_schema
from datetime import datetime
from django.db import transaction
from user.models import Client
from .services.delete_purchase_service import Delete_Purchase



def get_products(qs,name=None,brand=None):
    data = {}
    for product in qs:
        if product.amount > 0 and product.is_available:
            if product.product_type == 'Supplement':
                supplement = Supplements.objects.filter(pk=product.product_id).first()
                if supplement is not None:
                    if supplement.product.pk not in data:
                        if (name and ( name.lower() in supplement.product.name.lower())) or (brand and (brand.lower() in supplement.product.brand.lower())):
                            data[supplement.product.pk] = ProductSerializer(supplement.product).data
                        elif name is None and brand is None:
                            data[supplement.product.pk] = ProductSerializer(supplement.product).data
                
            elif product.product_type == 'Accessory':
                accessory = Accessories.objects.filter(pk=product.product_id).first()
                if accessory is not None:
                    if accessory.product.pk not in data:
                        
                        if (name and ( name.lower() in accessory.product.name.lower())) or (brand and (brand.lower() in accessory.product.brand.lower())):
                            
                            
                            data[accessory.product.pk] = ProductSerializer(accessory.product).data
                        elif name is None and brand is None:
                            
                            data[accessory.product.pk] = ProductSerializer(accessory.product).data
                            
            
            elif product.product_type == 'Meal':
                meal = Meals.objects.filter(pk=product.product_id).first()
                if meal is not None:
                    if meal.product.pk not in data:
                        if (name and ( name.lower() in meal.product.name.lower())):
                            
                            data[meal.product.pk] = ProductSerializer(meal.product).data
                        elif name is None and brand is None:
                            
                            data[meal.product.pk] = ProductSerializer(meal.product).data
    return data


def get_product_details(product_obj, name, brand):
    if product_obj is None:
        return None

    if (name and name.lower() in product_obj.product.name.lower()):
        return {
            'base_product_id': product_obj.product.pk,
            'name': product_obj.product.name,
            'brand': product_obj.product.brand,
            'description': product_obj.product.description
        }
    
    if name is None and brand is None:
        return {
            'base_product_id': product_obj.product.pk,
            'name': product_obj.product.name,
            'brand': product_obj.product.brand,
            'description': product_obj.product.description
        }
    
    return None


def get_private_products(qs, name=None, brand=None):
    valid_products = []
    for product in qs:
        product['branch'] = product['branch']['id']
        
        if product['amount'] > 0 and product['is_available']:
            product_details = None
            
            if product['product_type'] == 'Supplement':
                supplement = Supplements.objects.filter(pk=product['product_branch_id']).first()
                product_details = get_product_details(supplement, name, brand)
            
            elif product['product_type'] == 'Accessory':
                accessory = Accessories.objects.filter(pk=product['product_branch_id']).first()
                product_details = get_product_details(accessory, name, brand)
            
            elif product['product_type'] == 'Meal':
                meal = Meals.objects.filter(pk=product['product_branch_id']).first()
                product_details = get_product_details(meal, name, brand)
            
            if product_details:
                product.update(product_details)
                valid_products.append(product)
    
    return valid_products

 
class PublicStoreListAV(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        print(self.request.GET)
        name = self.request.GET.get('name', None)
        brand = self.request.GET.get('brand', None)
        qs = Branch_products.objects.filter(branch__gym__allow_public_products=True,branch__has_store=True)
        data = get_products(qs,name=name,brand=brand)
        return data
    
    
    @extend_schema( 
            summary='get products for public store' 
    )
        
    def get(self,request,*args, **kwargs):
        now = datetime.now().date()
        offers_qs = Offer.objects.filter(price_offers__isnull=False,start_date__lte=now,end_date__gte=now,
                                            is_deleted=False,branch__gym__allow_public_products=True,
                                            price_offers__objects__fee__isnull=True)
        offer_data =[]
        if len(request.GET) == 0:
            for offer in offers_qs:
                
                for product in offer.price_offers.objects.values():
                    amount_product = Branch_products.objects.get(pk=product['product_id']).amount
                    if amount_product > 0 :                
                        offer_details = Price_offersStoreSerializer(offer).data
                        offer_details['price_offer'].pop('price_offer_objects')
                        offer_details['price'] = offer_details['price_offer']['price']
                        offer_details.pop('price_offer')
                        offer_data.append(offer_details)
        products_data = self.get_queryset()
        data = {
            'products':products_data,
            'offers':offer_data
        }
            
        return Response(data,status=status.HTTP_200_OK)  
public_store = PublicStoreListAV.as_view()



@extend_schema(
    summary='get the details for products in public store' 
)
class Public_Product_DetailsRetrieveAV(generics.RetrieveAPIView):
    serializer_class = PublicStoreSerializer
    queryset = Product.objects.filter(is_deleted=False)
    
product_details = Public_Product_DetailsRetrieveAV.as_view()


@extend_schema(
    summary='get the details for products in private store' 
)
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


class PrivateStoreListAV(generics.ListAPIView):
    serializer_class = PrivateStoreSerializer
    
    def get_queryset(self):
        name = self.request.GET.get('name', None)
        brand = self.request.GET.get('brand', None)
        branch_id = self.kwargs.get('branch_id')
        qs = Branch_products.objects.filter(branch=branch_id,branch__has_store=True)
        serializer = Branch_productSerializer(qs,many=True).data
        data = get_private_products(serializer,name=name,brand=brand)
        return data
    
    
    @extend_schema(
    summary='get the products for private store' 
)
    def get(self,request,*args, **kwargs):
        try:
            now = datetime.now().date()
            offers_qs = Offer.objects.filter(price_offers__isnull=False,branch=kwargs['branch_id'],start_date__lte=now,end_date__gte=now,
                                                            is_deleted=False,price_offers__objects__fee__isnull=True)
            
            offer_data =[]
            if len(request.GET) == 0:
                for offer in offers_qs:
                    
                    for product in offer.price_offers.objects.values():
                        amount_product = Branch_products.objects.get(pk=product['product_id']).amount
                        if amount_product > 0 :
                            offer_details = Price_offersStoreSerializer(offer).data
                            offer_details['price_offer'].pop('price_offer_objects')
                            offer_details['price'] = offer_details['price_offer']['price']
                            offer_details.pop('price_offer')
                            offer_data.append(offer_details)
                            
            products_data = self.get_queryset()
            data = {
                'products':products_data,
                'offers':offer_data
            }
                    
            return Response(data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
private_store = PrivateStoreListAV.as_view()

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

class CLientPurchasingsListAV(generics.ListAPIView):
    serializer_class = PurchaseSerializer
    
    def get_queryset(self):
        try:
            client = Client.objects.get(user=self.request.user.pk)
            purchases = Purchase.objects.filter(client=client, is_deleted=False)
            return purchases
        except Client.DoesNotExist:
            raise ValueError('Client does not exist')
        
    @extend_schema(
        summary='return the client purchases history',
    )
    def get(self,request,*args,**kwargs):
        return super().get(request,*args,**kwargs)

purchases = CLientPurchasingsListAV.as_view()

class CLientPurchasingsDetailsAV(generics.DestroyAPIView):
    serializer_class = Public_Store_Purchase_Serializer 
    queryset = Purchase.objects.filter(is_deleted=False)
    
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
    serializer_class = EditPurchasesSerializer
    queryset = Purchase.objects.filter(is_deleted=False)
    
    @extend_schema(
        summary='return all the products and the price offers purchased for specific order',
        description = 'it has flag "allow update" that will either let the user update or delete specific product or not'
    )
    def get(self, request, *args, **kwargs):
        try:
            check = self.get_serializer(self.get_object()).data
            
            if check['products']is not None:
                return Response(check,status=status.HTTP_200_OK)
            return Response({'error':'you cannot edit your purchases'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

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
        summary='add products to purchase in update',
    )
    
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                request.data['purchase_id'] = kwargs.pop('pk')
                return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
add_products = AddProductsToPurchaseAV.as_view()



@extend_schema(
    summary='get the price offers details'
)
class PriceOfferRetreiveAV(generics.RetrieveAPIView):
    serializer_class = PriceOffersStoreSerializer
    queryset = Offer.objects.all()
price_offers_store = PriceOfferRetreiveAV.as_view()