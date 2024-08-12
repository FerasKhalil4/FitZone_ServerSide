from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import *
from .DataExamples import *
from community.paginations import Pagination
from django.db import transaction
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError

class OffersMixin():
    
    def check_overlapping_offers(self,start_date,end_date, offer_category, offer_category_value,branch_id,offer = None, **kwargs):
        
        base_query = Q(
                    start_date__lte = start_date,
                    end_date__gt = start_date,
                    ) | Q(
                        start_date__lt = end_date,
                        end_date__gte =end_date
                    ) | Q (
                        start_date__gt =start_date,
                        end_date__lt = end_date
                    )
                    
        base_query &=  Q(is_deleted = False, branch=branch_id)
      
        query = base_query & Q(**{f"percentage_offers__{offer_category}":offer_category_value })
                    
        for key , value in kwargs.items():
            query &= Q(**{f"percentage_offers__{key}":value})
            
        if offer is not None : 
            check_overlap_offers =Offer.objects.filter(query).exclude(pk = offer.pk)
        else: 
            check_overlap_offers =Offer.objects.filter(query)
            
        if check_overlap_offers.exists():
            raise serializers.ValidationError('Overlap offers for the created offer')                             
        return True
  
    def check_overlapping_price_offers(self,start_date,end_date, offer_category, offer_category_value,branch_id,offer= None, product_data = None):
        def get_product_query(query_ , data):
            query = Offer.objects
            for item in data:
                offer_category_value = item['product']
                query = query.filter(price_offers__objects__product=offer_category_value)
            if  offer is not None:
                query = query.filter(query_).distinct().exclude(pk = offer.pk)
            else : 
                query = query.filter(query_).distinct()
                
            return query
                
        base_query = Q(
            start_date__lte = start_date,
            end_date__gt = start_date,
            ) | Q(
                start_date__lt = end_date,
                end_date__gte =end_date
            ) | Q (
                start_date__gt =start_date,
                end_date__lt = end_date
            )
            
        base_query &= Q(is_deleted = False, branch=branch_id)
        query = base_query         
        
        if offer_category == 'product':
            check_overlap_offers= get_product_query(query, product_data)

            
        elif offer_category == 'fee':
            
                query &= Q(**{f"price_offers__objects__fee":offer_category_value })
                if offer is not None :                
                    check_overlap_offers =Offer.objects.filter(query).distinct().exclude(pk = offer.pk)
                else:
                    check_overlap_offers =Offer.objects.filter(query).distinct()
                    
        if check_overlap_offers.exists():
            raise serializers.ValidationError('Overlap offers for the created offer')  
          
        return True
        
    def update_Offer(self, offer_detail,start_date,end_date,branch_id,offer = None , offer_type = None):
    
        if 'fee' in offer_detail:
            if offer_type == 'PriceOffer':
                check = self.check_overlapping_price_offers(start_date, end_date,'fee', offer_detail['fee'],branch_id,offer = offer)
            elif offer_type == 'percentageOffer':
                check = self.check_overlapping_offers(start_date, end_date,'fee', offer_detail['fee'],branch_id)
            check = self.check_overlapping_offers(start_date, end_date,'fee',offer_detail['fee'],branch_id)
        elif 'class_id' in offer_detail:
            try:
                check =  self.check_overlapping_offers(start_date, end_date,'class_id', offer_detail['class_id'],branch_id)
            except Class_Scheduel.DoesNotExist:
                raise ValidationError({'error':'check on the class instance schdule'})

        elif 'category' in offer_detail:
            print(offer_detail)
            if 'supp_category' in offer_detail:
                check = self.check_overlapping_offers(start_date, end_date,'category', offer_detail['category'],branch_id,supp_category = offer_detail['supp_category'])
            else:
                check = self.check_overlapping_offers(start_date, end_date,'category', offer_detail['category'],branch_id)
        elif 'objects_data' in offer_detail:
            check =  self.check_overlapping_price_offers(start_date,end_date,'product',None,branch_id,offer = offer, product_data = offer_detail['objects_data'])
        return check
                
    def check_date(self,data) -> None:
        query = Q(
            start_date__lte = data['start_date'],
            end_date__gte = data['end_date'],
            class_id = data['offer_data']['class_id']
        )
        check = Class_Scheduel.objects.filter(query)
        print(check)
        if check.exists():
            pass
        else:
            raise ValidationError('check on the class schdeule')
        

          
    def SerializingCreatingPercentageOffers(self,data):
        try:
            offer_data = data.pop('offer_data', {})
            if 'supp_category' in offer_data:
                if  offer_data['supp_category'] == 0 :
                    offer_data.pop('supp_category',None)
            offer_serializer = OfferSerializer(data=data)
            offer_serializer.is_valid(raise_exception=True)
            offer = offer_serializer.save()
            offer_data['offer_id'] = offer.pk
            percentage_serialzier = PercentageOfferSerializer(data=offer_data)
            percentage_serialzier.is_valid(raise_exception=True)

            percentage_serialzier.save()
            
            return percentage_serialzier.data
        except Exception as e:
            raise serializers.ValidationError(str(e))
    def SerializingCreatingPriceOffers(self,data , offer_type):
        try:
            offer_data = data.pop('offer_data', {})
            offer_serializer = OfferSerializer(data=data)
            offer_serializer.is_valid(raise_exception=True)
            offer = offer_serializer.save()
            
            offer_data['offer_id'] = offer.pk
            
            price_serialzier = PriceOfferSerializer(data=offer_data)
            price_serialzier.is_valid(raise_exception=True)
            price_offer = price_serialzier.save()
            
            price_offer_data = {}
                
            if offer_type == 'product':
                objects_data = offer_data.get('objects_data')
                
                for object in objects_data:
                    
                    price_offer_data['offer'] = price_offer.pk
                    price_offer_data['product'] = object['product']
                    price_offer_data['number'] = object['number']

                    serializer = ObjectHasPriceOfferSerializer(data = price_offer_data) 
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    
            elif offer_type == 'fee':
                    price_offer_data['offer'] = price_offer.pk
                    price_offer_data['fee'] = offer_data['fee']
                    try:
                        Registration_Fee.objects.filter(pk=offer_data['fee'])
                    except Registration_Fee.DoesNotExist:
                        raise serializers.ValidationError('fee instance doesnot exist')
                    serializer = ObjectHasPriceOfferSerializer(data = price_offer_data) 
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    

            return serializer.data
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
@extend_schema(
summary="get all the offers related to a given branch"
)
class OffersListAV(generics.ListAPIView):
    serializer_class = OfferSerializer

    def get_queryset(self):
        branch_id = self.kwargs['branch_id']
        current_data = datetime.datetime.now().date()
        return Offer.objects.filter(is_deleted=False,branch_id = branch_id,
                                     end_date__gte = current_data)
    pagination_class = Pagination
    

offersList = OffersListAV.as_view()
            


@extend_schema(
summary="get all the fee percetnage offers related to a given branch"
)
class FeePercentageOfferListAV(OffersMixin,generics.ListCreateAPIView):
    
    serializer_class = OfferSerializer
    
    def get_queryset(self):
        
        branch_id = self.kwargs['branch_id']
        qs = Offer.objects.prefetch_related('percentage_offers').\
            filter(branch_id = branch_id ,is_deleted=False, percentage_offers__fee__isnull = False)
        return qs
    
    
    @extend_schema(
    summary="create fee percetnage offers related to a given branch",
    examples=fee_percentage_creation
    )
    def post(self, request,branch_id, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data 
                start_date = data['start_date']
                end_date = data['end_date']
                data['branch_id'] = branch_id
                if 'fee' not in data['offer_data']:
                    return Response({'message': 'No fee sent'}, status = status.HTTP_400_BAD_REQUEST)
                
                try:
                    gym_id = Branch.objects.get(id=branch_id).gym
                    Registration_Fee.objects.filter(gym_id = gym_id, pk=data['offer_data']['fee'])
                except Registration_Fee.DoesNotExist:
                    raise serializers.ValidationError('fee instance doesnot exist')
                
                self.check_overlapping_offers(start_date,end_date,"fee",data['offer_data']['fee'],branch_id)
                offer = self.SerializingCreatingPercentageOffers(data)
                return Response({'message':'offer created successfully','offer': offer}, status = status.HTTP_201_CREATED)
        except Exception as e:
            return Response ({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

feePercentageList = FeePercentageOfferListAV.as_view()
          
@extend_schema(
summary="get all the category percetnage offers related to a given branch"
)
class CategoryPercentageOfferListAV( OffersMixin , generics.ListCreateAPIView):

    
    serializer_class = OfferSerializer
    
    def get_queryset(self):
        branch_id = self.kwargs['branch_id']
        qs = Offer.objects.select_related('percentage_offers').\
            filter(branch_id = branch_id ,is_deleted=False, percentage_offers__category__isnull = False)
        return qs


    @extend_schema(
    summary="create fee percetnage offers related to a given branch",
    examples=category_percentage_creation
    )
    def post(self, request,branch_id, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data 
                start_date = data['start_date']
                end_date = data['end_date']
                data['branch_id'] = branch_id
                if 'category' not in data['offer_data']:
                    return Response({'message': 'No category sent'}, status = status.HTTP_400_BAD_REQUEST)
                
                try:
                    Category.objects.filter(pk=data['offer_data']['category'])
                except Category.DoesNotExist:
                    raise serializers.ValidationError('Category instance doesnot exist')
                
                if data['offer_data']['category'] == 1 and  data['offer_data']['supp_category']!= 0 : 
                    supp_category = data['offer_data']['supp_category']
                    self.check_overlapping_offers(start_date,end_date,"category",data['offer_data']['category'],branch_id
                                            ,percentage_offers__supp_category = supp_category)
                else:
                    
                    self.check_overlapping_offers(start_date,end_date,"category",data['offer_data']['category'],branch_id)
                    
                offer = self.SerializingCreatingPercentageOffers(data)
                return Response({'message':'offer created successfully','offer': offer}, status = status.HTTP_201_CREATED)
        except Exception as e:
            return Response ({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

categoryPercentageList = CategoryPercentageOfferListAV.as_view()



@extend_schema(
summary="get all the class percetnage offers related to a given branch"
)
class ClassPercentageOfferListAV(OffersMixin, generics.ListCreateAPIView):
    serializer_class = OfferSerializer
    
    def get_queryset(self):
        branch_id = self.kwargs['branch_id']
        qs = Offer.objects.select_related('percentage_offers').\
            filter(branch_id = branch_id ,is_deleted=False, percentage_offers__class_id__isnull = False)
        return qs


    @extend_schema(
    summary="create class percetnage offers related to a given branch",
    examples= class_offer_percetage
    )

    def post(self, request,branch_id, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data 
                start_date = data['start_date']
                end_date = data['end_date']
                data['branch_id']=branch_id
                if 'class_id' not in data['offer_data']:
                    return Response({'message': 'No classes sent'}, status = status.HTTP_400_BAD_REQUEST)
                try:
                    instance = Class_Scheduel.objects.get(id = data['offer_data']['class_id'],
                                                           class_id__branch_id = branch_id, start_date__lte = start_date, end_date__gte=end_date)
                except Class_Scheduel.DoesNotExist:
                    return Response({'error':'Class instance doesnot exist'},status=status.HTTP_400_BAD_REQUEST)
                
                self.check_overlapping_offers(start_date,end_date,"class_id",data['offer_data']['class_id'],branch_id)
                
                offer = self.SerializingCreatingPercentageOffers(data)
                return Response({'message':'offer created successfully','offer': offer}, status = status.HTTP_201_CREATED)
        except Exception as e:
            return Response ({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)  

classPercentageList = ClassPercentageOfferListAV.as_view()

@extend_schema(
summary="get all the fee price offers related to a given branch"
)
class FeePriceOfferListAV(OffersMixin, generics.ListCreateAPIView):
    serializer_class = OfferSerializer    
    
    def get_queryset(self):
            branch_id = self.kwargs['branch_id']
            qs = Offer.objects.select_related('price_offers').\
                    filter(branch_id = branch_id ,is_deleted=False, price_offers__objects__fee__isnull = False)
            return qs

    @extend_schema(
    summary="create fee price offers related to a given branch",
    examples=fee_price_offers
    )
    def post(self,request, branch_id,*args, **kwargs):
        try:
            with transaction.atomic():
            
                data = request.data 
                start_date = data['start_date']
                end_date = data['end_date']  
                data['branch_id'] = branch_id  
                if 'fee' not in data['offer_data']:
                    return Response({'message': 'No fee sent'}, status = status.HTTP_400_BAD_REQUEST)
                try:
                    gym_id = Branch.objects.get(pk=branch_id).gym
                    Registration_Fee.objects.filter(gym_id = gym_id, pk = data['offer_data']['fee'])
                except Registration_Fee.DoesNotExist as e:
                    return Response({'error':str(e)}, status = status.HTTP_400_BAD_REQUEST)
                self.check_overlapping_price_offers(start_date, end_date,'fee', data['offer_data']['fee'],branch_id)
                
                self.SerializingCreatingPriceOffers(data,'fee')
                
                return Response({'message':'offer created Successfully'}, status = status.HTTP_201_CREATED)
            
        except Exception as e : 
            return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
feePriceOfferList = FeePriceOfferListAV.as_view()



@extend_schema(
summary="get all the products price offers related to a given branch"
)
class ProdcutPriceOfferListAV(OffersMixin, generics.ListCreateAPIView):
    serializer_class = OfferSerializer
    
    def get_queryset(self):
        branch_id = self.kwargs['branch_id']
        qs = Offer.objects.select_related('price_offers').\
            filter(branch_id = branch_id ,is_deleted=False, price_offers__objects__product__isnull = False)
        return qs
    @extend_schema(
    summary="create products price offers related to a given branch",
    
    examples=prouduct_price_offers
    
    )
    def post(self,request,branch_id, *args, **kwargs):
        try:
            with transaction.atomic():
            
                data = request.data 
                start_date = data['start_date']
                end_date = data['end_date']    
                if 'objects_data' not in data['offer_data']:
                    return Response({'message': 'No products sent'}, status = status.HTTP_400_BAD_REQUEST)

                offer_data = data['offer_data']
                object_data = offer_data['objects_data']
                object_data_set = set(d['product'] for d in object_data)

                if len(object_data) != len(object_data_set):
                    return Response({'error':'please check on the send product there is duplications'}, status = status.HTTP_400_BAD_REQUEST)
                self.check_overlapping_price_offers(start_date,end_date,'product',None,data['branch_id'],product_data = object_data)
                
                self.SerializingCreatingPriceOffers(data,'product')
                    
                return Response({'message':'offer created Successfully'}, status = status.HTTP_201_CREATED)
            
        except Exception as e : 
            return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
productPriceOfferList = ProdcutPriceOfferListAV.as_view()
                    


class PercentageOfferDetailsAV(OffersMixin,generics.RetrieveUpdateAPIView):
    serializer_class=OfferSerializer
    queryset = Offer.objects.select_related('percentage_offers').filter(is_deleted=False)
    
        
    def get_object(self):
        try:
            return Offer.objects.select_related('percentage_offers').get(is_deleted=False, branch=self.kwargs['branch_id'],pk=self.kwargs['pk'],percentage_offers__isnull=False)
        except Offer.DoesNotExist:
            raise ValueError('offer does not exist')
            
    @extend_schema(
    summary="get specific percentage offer"
    )
    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer =self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
    summary="update specific percentage offer",
    examples=update_percentage_offer
    )
    def put(self, request,pk,branch_id, *args, **kwargs):
        try:
            with transaction.atomic():
                
                data = request.data 
                if 'class_id' in data['offer_data']:
                    print('check')
                    self.check_date(data)
                instance = Percentage_offer.objects.get(offer=pk)
                offer_detail = data.pop('offer_data',{})
                start_date = data['start_date']
                end_date = data['end_date'] 
                   
                self.update_Offer(offer_detail,start_date,end_date,branch_id,offer_type='percentageOffer')
                offer_serializer = OfferSerializer(instance, data=data, partial = True)
                offer_serializer.is_valid(raise_exception=True)
                offer_serializer.save()
                if offer_detail : 
                    offer_detail_instance= Percentage_offer.objects.get(offer_id = pk)
                    details_serializer = PercentageOfferSerializer(offer_detail_instance, data=offer_detail , partial = True)
                    details_serializer.is_valid(raise_exception=True)
                    details_serializer.save()

                return Response({'message':'offer updated successfully','offer': offer_serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
percentageDetails = PercentageOfferDetailsAV.as_view()



class PriceOfferDetailsAV(OffersMixin,generics.RetrieveUpdateAPIView):
    serializer_class = OfferSerializer
    queryset = Offer.objects.select_related('price_offers').filter(is_deleted=False)
    @extend_schema(
    summary="get specific price offer"
    )
    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer =self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
    summary="update specific price offer",
    examples=update_price_offers
    )
    def put(self, request,pk,branch_id, *args, **kwargs):
        try:
            with transaction.atomic():
  
                data = request.data 
                start_date = data['start_date']
                end_date = data['end_date']  
                instance = Offer.objects.select_related('price_offers').get(pk=pk)
                offer_detail = data.pop('offer_data',{})
                
                self.update_Offer(offer_detail,start_date,end_date,branch_id,offer = instance,offer_type='PriceOffer')
                
                
                objects_data = offer_detail.pop('objects_data',[])
                offer_serializer = OfferSerializer(instance, data=data, partial = True)
                offer_serializer.is_valid(raise_exception=True)
                offer_serializer.save()
                
                price_offer_instance = instance.price_offers
                if offer_detail : 
                    details_serializer = PriceOfferSerializer(price_offer_instance, data=offer_detail , partial = True)
                    details_serializer.is_valid(raise_exception=True)
                    details_serializer.save()
                    
                if objects_data :
                    for item in objects_data :
                        object_data_instance = ObjectHasPriceOffer.objects.get(offer = price_offer_instance.pk, product = item['product'])
                        instnace_details_serializer = ObjectHasPriceOfferSerializer(object_data_instance, data=item , partial = True)
                        
                        instnace_details_serializer.is_valid(raise_exception=True)
                        instnace_details_serializer.save()                        
                        
                return Response({'message':'offer updated successfully','offer': offer_serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Offer.DoesNotExist:
            return Response({'error':'Offer does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
priceDetails = PriceOfferDetailsAV.as_view()

@extend_schema(
summary="delete specific offer"
)
class DestroyOffersAV(generics.DestroyAPIView):
    queryset = Offer.objects.filter(is_deleted=False)
    serializer_class = OfferSerializer

destroyOffer = DestroyOffersAV.as_view()
        