from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import *
from .DataExample import *
from user.models import Client
from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import extend_schema
import datetime

class NutritionPlanListAV(generics.ListAPIView):
    serializer_class = NutritionPlanSerializer
    queryset = NutritionPlan.objects.all()
    
    @extend_schema(
        summary='get all the nutrition plans for the requested client'
    )
    def get (self, request, *args, **kwargs):
        try:
            today = datetime.datetime.now().date()
            query = Q (
                client=client,
                start__lte = today,
                end_date__gte = today,
                is_active=True
            )
            client = Client.objects.get(user = request.user.id)
            nutrition_plans = NutritionPlan.objects.get(client=client, is_active=True)
            serializer = NutritionPlanSerializer(nutrition_plans, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
NutritionPlanList = NutritionPlanListAV.as_view()


class NutritionPlanCreateAV(generics.CreateAPIView):
    serializer_class = NutritionPlanSerializer
    queryset = NutritionPlan.objects.all()
    
    @extend_schema(
        summary='create nutrition plan for specific client',
        examples=plan_create        
    )
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                client_id = kwargs['client_id']
                client = Client.objects.get(id=client_id)
                trainer = Trainer.objects.get(employee__user__pk=request.user.pk)
                data = request.data.copy()
                serializer = self.get_serializer(data=data, context={'client': client, 'trainer': trainer})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'message':'Nutrition Plan is Created Successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
NutritionPlanCreate = NutritionPlanCreateAV.as_view()
    
class UpdatePlanStatusAV(generics.UpdateAPIView):
    serializer_class=PlanStatusSerializer
    queryset=NutritionPlan.objects.all()
    
    @extend_schema(
        summary='update the status of a Nutrition plan',
        examples=[OpenApiExample(name='example1',
            value={'is_active':True}
        )]
    )
    def put(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                try:
                    client = Client.objects.get(user__id = request.user.id)
                except Client.DoesNotExist:
                    return  Response({'error':'client does not exist'},status=status.HTTP_400_BAD_REQUEST)
                instance = NutritionPlan.objects.get(client=client,start_date__lte = today, end_date__gte = today)
                serializer = self.get_serializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                return Response({'success':'plan status updated'},status=status.HTTP_200_OK)
        except Exception as e:
            return  Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

UpdatePlanStatus = UpdatePlanStatusAV.as_view()


class MealsCreateAV(generics.CreateAPIView):
    serializer_class = MealsSerializer
    queryset = Meals.objects.all()
    @extend_schema(
        summary="add meal to an existing meal type",
        examples=meal
    )
    def post(self,request,*args, **kwargs):
        try:
            
            meals_type_id = kwargs.pop('meals_type_id')
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(meals_type_id=meals_type_id)
            return Response({'success':'meal created successfully'},status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
MealsCreate = MealsCreateAV.as_view()


class MealsDetailsAV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MealsSerializer
    queryset = Meals.objects.all()
    @extend_schema(
        summary='Get a meal',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='Get a meal',
        examples=meal
    )
    def put(self, request,*args, **kwargs):
        try:
            return super().put(request, *args, **kwargs)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
    summary='Delete a meal',
    )
    def delete(self,request,*args, **kwargs):
        return super().delete(request,*args,**kwargs)

MealsDetails = MealsDetailsAV.as_view()

    
class MealsTypeCreateAV(generics.CreateAPIView):
    serializer_class = MealsTypeSerializer
    queryset = MealsType.objects.all()
    @extend_schema(
        summary='add another meal type',
        examples=meal
    )
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                schdeule = kwargs.pop('schdeule_id',None)
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(meals_schedule = schdeule)
                return Response({'success':'meal type created successfully'},status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
MealsTypeCreate = MealsTypeCreateAV.as_view()



@extend_schema(
        summary='delete meal type',
    )
class MealsTypeDeleteAV(generics.DestroyAPIView):
    serializer_class = MealsTypeSerializer
    queryset = MealsType.objects.all()
    
MealsTypeDelete = MealsTypeDeleteAV.as_view()

