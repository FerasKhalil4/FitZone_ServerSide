from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from .serialziers import *
from .filters import Client_TrainerFilter
from .DataExamples import *
from gym.seriailizers import TrainerSerialzier,ShiftSerializer
import datetime
from dateutil.relativedelta import relativedelta
from plans.serializers import ClientTrainingSerializer,Client_Trianing_Plan,Gym_plans_ClientsSerializer,Gym_plans_Clients
from django.db.models import Q
from nutrition.serializers import NutritionPlan,NutritionPlanSerializer
from wallet.models import Wallet, Wallet_Deposit
class ClientsListAV(generics.ListAPIView):
    serializer_class = Client_TrainerSerializer
    queryset = Client_Trainer.objects.filter(registration_status = 'pending')
    filter_backends = [DjangoFilterBackend]
    filterset_class = Client_TrainerFilter
    @extend_schema(
            summary = 'get the clients registered with the trainer'
        )
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            trainer = Trainer.objects.get(employee__user = user)
            qs = self.filter_queryset(self.get_queryset())
            qs = qs.filter(trainer=trainer)
            serializer = self.get_serializer(qs,many=True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status =status.HTTP_400_BAD_REQUEST)
            
clientlist = ClientsListAV.as_view()


class ApproveClientsAV(generics.UpdateAPIView):
    serializer_class = Client_TrainerSerializer
    queryset = Client_Trainer.objects.filter(registration_status = 'pending')

        
    @extend_schema(
        summary = 'approve or reject specific pending client',
        examples=approve_client
    )
    def put(self, request, *args, **kwargs):
        try:
            with transaction.atomic():                
                data=request.data
                instance = self.get_object()
                wallet = Wallet.objects.get(client_id=instance.client.pk) 
                
                
                if instance.registration_status == 'accepted':
                    return Response({'error':'you cant update the status of this client'},status = status.HTTP_400_BAD_REQUEST)
                
                user = request.user
                trainer = Trainer.objects.get(employee__user = user)
                
                fee = trainer.private_training_price if data['registration_type'] == 'private' else trainer.online_training_price
                
                if trainer != instance.trainer :
                    return Response({'error':'invalid client'}, status=status.HTTP_400_BAD_REQUEST)   
                
                if data['registration_status'] != 'rejected':
                        wallet.balance += fee
                        wallet.save()
                        
                        Wallet_Deposit.objects.create(
                            client = instance.client.pk,
                            amount = fee,
                            tranasaction_type='retrieve'
                        )
                        
                        return Response({'success':'client request rejected'}, status=status.HTTP_400_BAD_REQUEST)
                
                if data['registration_status'] != 'rejected':
                    start_date = datetime.datetime.now().date()
                    end_date = start_date + relativedelta(months=1)
                    data['start_date'] = start_date 
                    data['end_date'] = end_date

                serializer = self.get_serializer(instance, data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':'client status updated'},status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status = status.HTTP_400_BAD_REQUEST)

approveClients = ApproveClientsAV.as_view()


class ClientPlanRetrieveAV(generics.RetrieveAPIView):
    queryset = Client_Trianing_Plan.objects.all()
    serializer_class = ClientTrainingSerializer
    
    @extend_schema(
        summary="get the current training plan related to the client",
   )
    def get(self, request, *args, **kwargs):
        try:
            today = datetime.datetime.now().date()
            client = kwargs.get('client_id')
            query = Q(
                client_id=client,
                start_date__lte=today,
                end_date__gte=today,
                is_active=True
            )
            
            client_plan= Client_Trianing_Plan.objects.filter(query)
            gym_plan = Gym_plans_Clients.objects.filter(query)
            nutrition_plan = NutritionPlan.objects.filter(query)
            
            client_plan = client_plan.first() if client_plan.exists() else None
            gym_plan = gym_plan.first() if gym_plan.exists() else None
            nutrition_plan = nutrition_plan.first() if nutrition_plan.exists() else None
            serilaizer_client_plan = {}
            gym_plan_serilaizer = {}
            nutrition_plan_serializer = {}
            if client_plan is not None:
                serilaizer_client_plan = ClientTrainingSerializer(client_plan).data
                serilaizer_client_plan.pop('trainer',None) 
            if gym_plan is not None:
                gym_plan_serilaizer = Gym_plans_ClientsSerializer(gym_plan).data 
            if nutrition_plan is not None:
                nutrition_plan_serializer = NutritionPlanSerializer(nutrition_plan).data 
                nutrition_plan_serializer.pop('trainer',None)
            return Response ({'client_private_plan':serilaizer_client_plan,
                              'client_gym_plan':gym_plan_serilaizer,
                              'client_nutrition_plan': nutrition_plan_serializer},status=status.HTTP_200_OK)
        except Exception as e :
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

ClientTrainingPlanRetrieve = ClientPlanRetrieveAV.as_view()


class TrainerGroupsListAV(generics.ListCreateAPIView):
    serializer_class = TrainerGroupsSerializer
    queryset = TrainerGroups.objects.all()
    
    @extend_schema(
        summary='get trainer groups',
    )
    def get(self, request, *args, **kwargs): 
        return super().get(request, *args, **kwargs)
        
    @extend_schema(
        summary='create a group',
        examples=group
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            with transaction.atomic():
                trainer = Trainer.objects.get(employee__user=request.user)
                data['trainer'] = trainer.id
                session_length = data.pop('session_length')
                data['end_hour'] =datetime.datetime.strftime(datetime.datetime.strptime(data['start_hour'],'%H:%M:%S') 
                                                             + datetime.timedelta(minutes=session_length),'%H:%M:%S' )
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':'group is created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e: 
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

trainerGroupsList = TrainerGroupsListAV.as_view()

class TrainerGroupsDetailAV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TrainerGroupsSerializer
    queryset = TrainerGroups.objects.all()
    @extend_schema(
        summary='get a group',
    )
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='update a group',
        examples=group
    )
    def put(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                data = request.data
                trainer = Trainer.objects.get(employee__user=request.user)
                data['trainer'] = trainer.id
                session_length = data.pop('session_length')
                data['end_hour'] =datetime.datetime.strftime(datetime.datetime.strptime(data['start_hour'],'%H:%M:%S') 
                                                                + datetime.timedelta(minutes=session_length),'%H:%M:%S' )
                serializer = self.get_serializer(instance, data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':'group updated successfully'}, status =status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary='delete a group',
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
        
TrainerGroupsDetail = TrainerGroupsDetailAV.as_view()

class ClientDetailsAV(generics.RetrieveAPIView):
    serializer_class =  Client_TrainerSerializer
    queryset = Client_Trainer.objects.all()
    
    @extend_schema(
        summary='get client details'
    )
    def get(self, request, *args, **kwargs):
        print(kwargs)
        print(kwargs['client_id'])
        try:
            try:
                trainer = Trainer.objects.get(employee__user = request.user)
            except Trainer.DoesNotExist:
                return Response({'error':'trainer not found'}, status=status.HTTP_404_NOT_FOUND)
            now =  datetime.datetime.now().date()
            try:
                instance = Client_Trainer.objects.get(client=kwargs['client_id'],trainer=trainer,start_date__lte = now, end_date__gte = now)
            except Client_Trainer.DoesNotExist:
                return Response({'error':'client not found for this trainer or training period'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
client_details = ClientDetailsAV.as_view()

class TrainerProfileAV(generics.RetrieveAPIView):
    serializer_class = TrainerSerialzier
    queryset = Trainer.objects.all()
    
    @extend_schema(
        summary='get trainer profile'
    )
    def get(self, request, *args, **kwargs):
        try:
            obj = Trainer.objects.get(employee__user = request.user.pk)
            shifts = Shifts.objects.filter(employee__user=request.user.pk,is_active=True)
            return Response({
                'profile_data':self.get_serializer(obj).data,
                'shifts':ShiftSerializer(shifts,many=True).data
                             }, status=status.HTTP_200_OK)
        except Trainer.DoesNotExist:
            return Response({'error':'trainer not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
trainer_profile = TrainerProfileAV.as_view()