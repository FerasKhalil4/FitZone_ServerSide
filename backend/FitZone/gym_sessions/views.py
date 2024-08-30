from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Gym_Subscription, Branch_Sessions, Client, ValidationError 
from .serializers import Client_BranchSerializer
from .DataExamples import *
from equipments.models import Diagram
from equipments.serializers import  DiagramSerialzier
from trainer.models import Client_Trainer
from gym.models import Branch, Woman_Training_Hours
from plans.models import Gym_plans_Clients, Client_Trianing_Plan, Workout
from plans.serializers import WorkoutSerializer 
from django.db.models import Q
from datetime import datetime
from drf_spectacular.utils import extend_schema
from django.db import transaction
from django.core.exceptions import ValidationError



class SessionMixin():
    
    @staticmethod 
    def get_query(client):
        today_date = datetime.now().date()

        return Q(
        client =client.pk,
        start_date__lte = today_date,
        end_date__gte = today_date,
        is_active = True,
        )
        
    @staticmethod
    def check_women_hours(branch, gender):
        today = datetime.now().strftime('%A').lower()
        current_hour = datetime.now().time()
        women_hours = Woman_Training_Hours.objects.filter(gym=branch.gym)
        
        for hour in women_hours :

            if (hour.day_of_week.lower() == today )and (gender == True) and( hour.start_hour <= current_hour) and (hour.end_hour >= current_hour):
                raise ValidationError({'error':'you cant start your session now its women traingin hours'})
            
    @staticmethod
    def check_sub_one_branch_access(client,branch_id):

        query = SessionMixin.get_query(client)
        query &= Q(
        branch = branch_id,
        )
        
        try:
            check = Gym_Subscription.objects.get(query)
        except Gym_Subscription.DoesNotExist:
            raise ValidationError({'error':'user is not registered in any gym currently'})
        if check:
            workout = SessionMixin.get_client_todays_workout(client)
            print(workout)
            if workout is not None:
                if workout.name == 'Rest':
                    raise ValidationError({'error':'you cannot train today it is you rest day'})
                return workout
        return None
    
    @staticmethod
    def check_sub_multi_gym_access(client,branch):
        
        base_query = SessionMixin.get_query(client)
        
        try:
            check = Gym_Subscription.objects.get(base_query)
        except Gym_Subscription.DoesNotExist:
            raise ValidationError({'error':'user is not registered in any gym currently'})
        gym = check.branch.gym
        
        if gym == branch.gym :
            workout = SessionMixin.get_client_todays_workout(client)
            if workout is not None:
                if workout.name == 'Rest':
                    raise ValidationError({'error':'you cannot train today it is you rest day'})
                return workout
        return None

    @staticmethod
    def get_client_todays_workout(client):
        query = SessionMixin.get_query(client)
        today_number = datetime.now().day % 7 
        
        gym_training_plan =Gym_plans_Clients.objects.filter(query)
        
        if gym_training_plan.exists():
            training_plan = gym_training_plan.first().gym_training_plan.training_plan

        client_training_plan = Client_Trianing_Plan.objects.filter(query)
        
        if client_training_plan.exists():
            training_plan = client_training_plan.first().training_plan
            
        try:
            workout = Workout.objects.filter(training_plan = training_plan)
            ordered_workout = workout.get(order=today_number)
            
            if ordered_workout.same_as_order is not None:
                ordered_workout = workout.get(order = ordered_workout.same_as_order )
            return ordered_workout
        except Workout.DoesNotExist:
            return None
        except :
            return None
            
    @staticmethod 
    def get_diagram(user,branch_id):
        now = datetime.now().date()
        client = Client.objects.get(user=user)
        diagram =  Diagram.objects.filter(branch=branch_id)
        
        try:
            trainer = Client_Trainer.objects.get(client=client,start_date__lte=now, end_date__gte=now,registration_status='accepted').trainer
        except Client_Trainer.DoesNotExist:
            trainer = None
            
        data = DiagramSerialzier(diagram,many=True,context={'trainer':trainer}).data if trainer is not None\
                                                else DiagramSerialzier(diagram,many=True).data
                                                
        return data
    
            
@api_view(['GET'])
@extend_schema(
    summary='check if the user can start his session in the branch'
)
def check_Session(request,*args, **kwargs):
    if request.method == 'GET' and request.user.is_authenticated and request.user.role == 5:
        try:
            with transaction.atomic():
                branch_id = kwargs['branch_id']
                
                user_gender = request.user.gender
                try:
                    branch = Branch.objects.get(pk=branch_id)
                except Branch.DoesNotExist:
                    return Response({'error':'branch does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                
                SessionMixin.check_women_hours(branch, user_gender)
                
                try:
                    client = Client.objects.get(user=request.user.pk)
                except Client.DoesNotExist:
                    return Response({'error':'client does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                print(client)
                Branch_Sessions.objects.create(
                    client = client,
                    branch = branch,
                )
                diagram = SessionMixin.get_diagram(request.user, kwargs['branch_id'])
                
                if branch.gym.allow_branches_access == False :
                    workout = SessionMixin.check_sub_one_branch_access(client,branch_id)
                    
                else :
                    workout = SessionMixin.check_sub_multi_gym_access(client,branch)
                    
                if workout is not None:
                    return Response({'workout':WorkoutSerializer(workout).data
                                        ,'diagram':diagram
                                        }, status=status.HTTP_200_OK)
                return Response({'success':'you can start your session now',
                                    'diagram':diagram}, status=status.HTTP_200_OK)
                                        
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    else :
        return Response({'error':'user is not authenticated'},status=status.HTTP_400_BAD_REQUEST)
    
    
        
class SubscribtionsListAV(generics.ListCreateAPIView):
    
    serializer_class = Client_BranchSerializer
    queryset = Gym_Subscription.objects.all()
    
    @extend_schema(
        summary='get all the client history subscriptions'
    )
    def get(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(user=self.request.user.pk)
            registrations = Gym_Subscription.objects.filter(client=client.pk).order_by('-id')
            return Response(Client_BranchSerializer(registrations,many=True).data,status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response({'error':'Client does not exist'},status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary='subscripe in specific branch',
        examples=subscription
    )
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                client = Client.objects.get(user=request.user.pk)
                request.data['client'] = client.pk
                request.data['branch'] = kwargs['branch_id']
                return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
subscribtion_List = SubscribtionsListAV.as_view()


class SubscribtionsDetailsAV(generics.RetrieveUpdateDestroyAPIView):
    
    serializer_class = Client_BranchSerializer
    queryset = Gym_Subscription.objects.all()
    
    @extend_schema(
        summary='get the current subscription details'
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)            
        except Gym_Subscription.DoesNotExist:
            return Response({'error': 'user is not registered in any gym'}, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        summary='update the current subscription',
        examples=subscription
    )
    
    def put(self,request,*args, **kwargs):
        try:
            with transaction.atomic():
                
                client = Client.objects.get(user=request.user.pk)
                request.data['client'] = client.pk
                request.data['branch'] =self.get_object().branch.pk
                return super().update(request,*args, **kwargs,instance=self.get_object())
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
    @extend_schema(
        summary='cancel the current subscription'
    )
    def delete(self,request,*args, **kwargs):
        try:
            with transaction.atomic():
                return super().delete(request, *args, **kwargs)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
    
subscribtion_details = SubscribtionsDetailsAV.as_view()

class Diagram_Session(generics.ListAPIView):
    serializer_class = DiagramSerialzier
    queryset = Diagram.objects.all()
    
    @extend_schema(
        summary='get the diagrams for client',
    )
    def get(self, request, *args, **kwargs):
        
        now = datetime.now().date()
        client = Client.objects.get(user=request.user)
        diagram =  Diagram.objects.filter(branch=kwargs['branch_id'])
        
        try:
            trainer = Client_Trainer.objects.get(client=client,start_date__lte=now, end_date__gte=now,registration_status='accepted').trainer
        except Client_Trainer.DoesNotExist:
            trainer = None
        data = self.get_serializer(diagram,many=True,context={'trainer':trainer}).data if trainer is not None\
                                                        else self.get_serializer(diagram,many=True).data
        return Response(data, status=status.HTTP_200_OK)
    
diagrams = Diagram_Session.as_view()       