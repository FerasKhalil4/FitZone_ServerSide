from rest_framework import generics, status ,serializers
from rest_framework.response import Response
from .models import *
from .serializers import *
from wallet.models import Wallet, Wallet_Deposit
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
                employee = Employee.objects.get(user=request.user.pk)
                class_scheduel = Class_Scheduel.objects.filter(class_id = pk , start_date__lte = current_date , end_date__gte = current_date )
                Flag = True
                clients_to_refund = []
                
                for schedule in class_scheduel:
                    enrolled_clients = Client_Class.objects.filter(class_id = schedule.pk)
                    if len(enrolled_clients) >= (math.ceil(schedule.allowed_number_for_class / 2)):
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
                    cut_percentage = Branch.objects.get(pk=class_data.branch.pk).gym.cut_percentage
                    
                    for client_data in clients_to_refund:
                        amount = 0 if cut_percentage is None else class_data.registration_fee  -  ((class_data.registration_fee / 100) * cut_percentage)
                        client_data.retieved_money = amount
                        client_data.retrieved_reason = "Class Closed"
                        client_data.save()
                        
                        wallet = Wallet.objects.get(client = client_data.client)
                        wallet.balance += amount
                        wallet.save()
                        
                        Wallet_Deposit.objects.create(employee = employee ,client = client_data.client, amount = amount)
                        
                        
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
    queryset = Class_Scheduel.objects.all()

    
    def get(self, request, *args, **kwargs):
        try:
            class_id = kwargs.get('pk')
            current_date = datetime.datetime.now().date()
            qs = Class_Scheduel.objects.filter(class_id = class_id , start_date__lte = current_date , end_date__gte = current_date)
            serializer = self.get_serializer(qs,many=True)
            qs = serializer.data
            return Response({'data':qs}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response ({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self,request,pk,*args, **kwargs):
        try:
            check = Class_Scheduel.objects.get(class_id=pk)
            
            data = request.data
            data['class_id'] = pk   
            scheduleSerializer = Class_ScheduelSerializer(data=data,context={'request':request,'branch_id':data['branch_id']})
            scheduleSerializer.is_valid(raise_exception=True)
            scheduleSerializer.validated_data['class_id'] = Classes.objects.get(pk=data['class_id'])
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
    queryset = Class_Scheduel.objects.all()
    
    def update(self, request, pk, *args, **kwargs):
        try:
            data = request.data
            schedule_instance = self.get_object()
            
            if 'hall' in data or 'start_date' in data or 'end_date' in data or 'start_time' in data or 'end_time' in data or 'trainer_id' in data:
               
                check = Client_Class.objects.filter(pk = schedule_instance.pk)
              
                if len(check) > (schedule_instance.allowed_number_for_class / 2):
                    return Response({'message':'sechdule Cant be Updated there is clients already Booked at this time'}) 
             
             
                number_of_days = (schedule_instance.end_date - schedule_instance.start_date).days
                middle_day = math.ceil(number_of_days / 2)
                middle_day_date = schedule_instance.start_date + datetime.timedelta(days=middle_day)
                current_date = datetime.datetime.now().date()
                
                if current_date >  middle_day_date :
                    return Response({'error':'you cannot delete this schedule'},status=status.HTTP_400_BAD_REQUEST)
                
            serializer = Class_ScheduelSerializer(schedule_instance, data=request.data,context={'request':request,'branch_id':data['branch_id']} ,partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message':'schedule has Updated successfully','data':serializer.data}
            ,status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error':str(e)})
    
    def destroy(self, request, pk, *args, **kwargs):
        
        try:
            with transaction.atomic():
                schedule_instance = self.get_object()
                class_ = Classes.objects.get(pk = schedule_instance.class_id.pk)
                check = Client_Class.objects.filter(pk = schedule_instance.pk)
                employee = Employee.objects.get(user=request.user.pk)
                cut_percentage = Branch.objects.get(pk=class_.branch.pk).gym.cut_percentage
                
                if len(check) >= (math.ceil(schedule_instance.allowed_number_for_class / 2)):
                    return Response({'error':'you cannot delete this schedule'},status=status.HTTP_400_BAD_REQUEST)
                
                number_of_days = (schedule_instance.end_date - schedule_instance.start_date).days
                middle_day = math.ceil(number_of_days / 2)
                middle_day_date = schedule_instance.start_date + datetime.timedelta(days=middle_day)
                current_date = datetime.datetime.now().date()
                
                if current_date >  middle_day_date :
                    return Response({'error':'you cannot delete this schedule'},status=status.HTTP_400_BAD_REQUEST)

                for client_data in check :
                    amount = 0 if cut_percentage is None else  class_.registration_fee  -  ((class_.registration_fee / 100) * cut_percentage)
                    client_data.retieved_money = amount
                    client_data.retrieved_reason = "Time for this class is Closed"
                    client_data.save()
                    
                    
                    wallet = Wallet.objects.get(client = client_data.client)
                    wallet.balance += amount
                    wallet.save()
                    
                    Wallet_Deposit.objects.create(employee = employee ,client = client_data.client, amount = amount)
                
                schedule_instance.delete()
                
                return Response({'message':' Time in schedule has deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error':str(e)})
Class_ScheduleDetails = ClassScheduleDetailsAv.as_view()

        
        
        