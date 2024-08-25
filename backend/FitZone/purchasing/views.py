from rest_framework import generics,status
from store.models import Product
from store.serializers import PublicStoreSerializer,PrivateStoreSerializer
from rest_framework.response import Response
from django.core.cache import cache
from offers.models import Offer
from gym.models import Branch ,Gym
from offers.serializers import Price_offersStoreSerializer
from drf_spectacular.utils import extend_schema
from datetime import datetime


class PublicStoreListAV(generics.ListAPIView):
    serializer_class = PublicStoreSerializer
    queryset = Product.objects.filter(is_deleted=False)
    @extend_schema(
        summary='get products for public store'
    )
    def get(self,request,*args, **kwargs):
        cache_key = 'public_store_products'
        data = cache.get(cache_key)
        if not data:
            now = datetime.now().date()
            offers_qs = Offer.objects.filter(price_offers__isnull=False,start_date__lte=now,end_date__gte=now,is_deleted=False)
            offers_data = Price_offersStoreSerializer(offers_qs,many=True).data
            qs = self.get_queryset()
            products_data = self.get_serializer(qs,many=True).data
            data = {
                'products':products_data,
                'offers':offers_data
            }
            cache.set(cache_key,data,timeout=60*45)            
        return Response(data,status=status.HTTP_200_OK)  


def filtering_data(data,filtering):
    products = data.get('products').get('products').get(filtering)
    offers = data.get('offers')
    data = {
    'products':products,
    'offers':offers
                }
    return data
public_store = PublicStoreListAV.as_view()

class PrivateStoreLisAV(generics.ListAPIView):
    serializer_class = PrivateStoreSerializer
    queryset = Gym.objects.filter(is_deleted=False)
    
    def get(self,request,*args, **kwargs):
        try:
            gym= Branch.objects.get(pk=kwargs['branch_id']).gym
            
            cache_key = f'private_store_products{gym.pk}'
            data = cache.get(cache_key)
            
            filtering = request.GET.get('product_type', None)
            
            if filtering is not None and data is not None: 
                data = filtering_data(data,filtering)
                return Response(data,status=status.HTTP_200_OK)
                
            if not data:
                now = datetime.now().date()
                offers_qs = Offer.objects.filter(price_offers__isnull=False,branch=kwargs['branch_id'],start_date__lte=now,end_date__gte=now,is_deleted=False)
                offers_data = Price_offersStoreSerializer(offers_qs,many=True).data
                products_data = self.get_serializer(gym).data
                data = {
                    'products':products_data,
                    'offers':offers_data
                }
                cache.set(cache_key,data,timeout=60*45)  
                if filtering:   
                    data = filtering_data(data,filtering)
                       
            return Response(data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
private_store = PrivateStoreLisAV.as_view()
    