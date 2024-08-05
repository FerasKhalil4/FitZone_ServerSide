from rest_framework import generics, status ,serializers
from rest_framework.response import Response
from .models import *
from .serializers import *
from points.models import Points
import math, datetime
from django.db import transaction
import json
def get_product_points(price):
    activity = Points.objects.get(activity="Product points percentage").points_percentage
    return math.ceil(price / activity)

class ClassesListAV(generics.ListCreateAPIView):
    serializer_class = ClassesSerializer
    
    def get_queryset(self):
        branch_id = self.kwargs.get('branch_id')
        current_date = datetime.datetime.now().date()
        query = Q(
            is_deleted=False,
            branch__is_active=True,
            branch_id=branch_id,
            scheduel__end_date__gte=current_date
        )
        return Classes.objects.filter(query)
    
    
    def post(self, request,branch_id, *args, **kwargs):
            try:
                with transaction.atomic():
                        data = request.data.dict()
                        schedule_data = request.data.get('schedule')
                        if schedule_data:
                            if isinstance(schedule_data, str):
                                try:
                                    schedule_data = json.loads(schedule_data.replace("'", "\""))
                                except json.JSONDecodeError:
                                    return Response({"error": "Invalid format for schedule"}, status=status.HTTP_400_BAD_REQUEST)
                        
                        data['schedule'] = schedule_data
                        serializer = CreateClassSerializer(data=data,context = {'request':request,'branch_id':branch_id})
                        if serializer.is_valid(raise_exception=True):
                            serializer.save()
                            
                return Response({'message':'class created successfully'}, status=status.HTTP_201_CREATED)
                            
            except Exception as e:
                return Response(str(e),status=status.HTTP_400_BAD_REQUEST)
                
classesListAV = ClassesListAV.as_view()
    
class ClassesDetailAV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassesSerializer
    queryset = Classes.objects.filter(is_deleted = False)
    
    
    def update(self,request, pk, *args , **kwargs):
        try:
                class_data = Classes.objects.get(pk = pk)
                serializer = self.get_serializer(class_data, data = request.data ,context = {'request': request,
                                                                                            'instance':class_data},partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                return Response({'success':'class updated successfully'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self,request, pk, *args , **kwargs):
        try:
            with transaction.atomic():
                class_data = Classes.objects.get(pk = pk)
                current_date = datetime.datetime.now().date()
                class_scheduel = Class_Scheduel.objects.filter(class_ = pk , start_date__lte = current_date , end_date__gte = current_date )
                Flag = True
                clients_to_refund = []
                
                for schedule in class_scheduel:
                    enrolled_clients = Client_Class.objects.filter(class_id = schedule.pk)
                    if len(enrolled_clients) >= (schedule.allowed_number_for_class / 2):
                        Flag = False
                        break 
                    
                    number_of_days = (schedule.end_date - schedule.start_date).days
                    middle_day = math.ceil(number_of_days / 2)
                    middle_day_date = schedule.start_date + datetime.timedelta(days=middle_day)
                    
                    if current_date >  middle_day_date :
                            Flag = False
                            break
                    clients_to_refund.extend(enrolled_clients)
                    
                if Flag :
                    for client_data in clients_to_refund:
                        client_data.client.retieved_money = class_data.registration_fee
                        client_data.client.retrieved_reason = "Class Closed"
                        client_data.client.save()

                    class_data.delete()

                    return Response({'message':'data deleted Successfully'}, status=status.HTTP_204_NO_CONTENT)
                
                else:
                    return Response({'message':'Class cannot be deleted: customer count exceeded the half number of the class max number \
                                    or past midpoint'}, 
                                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e))
classesDetailAV = ClassesDetailAV.as_view()

class ClassScheduleListAV(generics.ListCreateAPIView):
    serializer_class = Class_ScheduelSerializer
    
    def get_queryset(self):
        class_id = self.request.data.get('pk')
        current_date = datetime.datetime.now().date()
        return Class_Scheduel.objects.filter(class_ = class_id , start_date__lte = current_date , end_date__gte = current_date )
    
    def post(self,request,pk,*args, **kwargs):
        try:
            
            check = Class_Scheduel.objects.get(pk=pk)
            
            data = request.data
            data['class_id'] = pk
            
            scheduleSerializer = Class_ScheduelSerializer(data=data)
            scheduleSerializer.is_valid(raise_exception=True)
            scheduleSerializer.save()
                        
            return Response({'message':'schedule has add-ons successfully','data':scheduleSerializer.data}
                            ,status=status.HTTP_201_CREATED)
                        
        except Exception as e:
            return Response({'error':str(e)})
        except Class_Scheduel.DoesNotExist as e:
            return Response({'message':str(e)},status = status.HTTP_404_NOT_FOUND)
Class_ScheduleList = ClassScheduleListAV.as_view()
        
class ClassScheduleDetailsAv(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = Class_ScheduelSerializer
    
    def update(self, request, pk, *args, **kwargs):
        try:
            data = request.data
            schedule_instance = self.get_object()
            
            if 'hall' in data or 'start_date' in data or 'end_date' in data or 'start_time' in data or 'end_time' in data or 'trainer_id' in data:
               
                check = Client_Class.objects.filter(pk = schedule_instance.pk)
              
                if len(check) > (schedule_instance.allowed_number_for_class / 2):
                    return Response({'message':'sechdule Cant be Updated there is clients already Booked at this time'}) 
             
            serializer = Class_ScheduelSerializer(schedule_instance, data=request.data, partial=True)
            serializer.is_valid(raise_exceptions=True)
            serializer.save()
            return Response({'message':'schedule has Updated successfully','data':serializer.data}
            ,status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error':str(e)})
    
    def destroy(self, request, pk, *args, **kwargs):
        schedule_instance = self.get_object()
        class_ = Classes.objects.get(pk = schedule_instance.pk)
        check = Client_Class.objects.filter(pk = schedule_instance.pk)
            
        if len(check) > (schedule_instance.allowed_number_for_class / 2):
            return Response({'message':'sechdule Cant be Updated there is clients already Booked at this time'}) 
        
        for client_data in check :
            client_data.client.retieved_money = class_.registration_fee
            client_data.client.retrieved_reason = "Time for this class is Closed"
            client_data.client.save()
        
        schedule_instance.delete()
        
        return Response({'message':' Time in schedule has deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

Class_ScheduleDetails = ClassScheduleDetailsAv.as_view()

        
        
        