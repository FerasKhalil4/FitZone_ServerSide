from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Gym_Subscription, Branch_Sessions, Client, ValidationError
from .serializers import Client_BranchSerializer, Branch_SessionsSerializer
from .DataExamples import *
from equipments.models import Diagram
from gym.models import Branch, Woman_Training_Hours
from equipments.serializers import DiagramSerialzier
from django.db.models import Q
import datetime
from drf_spectacular.utils import extend_schema
from django.db import transaction



now = datetime.datetime.now()

@api_view(['GET'])
@extend_schema(
    summary='check if the user can start his session in the branch'
)
def check_Session(request,*args, **kwargs):
    if request.method == 'GET' and request.user.is_authenticated and request.user.role == 5:
        try:
            branch_id = kwargs['branch_id']
            
            try:
                branch = Branch.objects.get(pk=branch_id)
            except Branch.DoesNotExist:
                return Response({'error':'branch does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            today_date = now.date()
            today = now.strftime('%A').lower()
            current_hour = now.time()
            
            women_hours = Woman_Training_Hours.objects.filter(gym=branch.gym)
            
            for hour in women_hours :
                if hour.day_of_week.lower() == today and request.user.gender == True and hour.start_hour <= current_hour and hour.end_hour >= current_hour:
                    return Response({'error':'you cant start your session now its women traingin hours'}, status=status.HTTP_400_BAD_REQUEST)
            
            base_query = Q(
                    user = request.user.pk,
                    start_date__lte = today_date,
                    end_date__gte = today_date,
                    is_active = True,
                )
            
            if branch.gym.allow_branches_access == False :
                
                base_query &= Q(
                    branch = branch_id,
                )
                check = Gym_Subscription.objects.filter(base_query)   
                
                if check.exists():
                    diagrams = Diagram.objects.filter(branch=branch_id)
                    return Response(DiagramSerialzier(diagrams,many=True).data,status=status.HTTP_200_OK)
                
                else:
                    return Response({'error':'your gym membership is expired'},status=status.HTTP_400_BAD_REQUEST)
            else :
                
                try:
                    check = Gym_Subscription.objects.get(base_query)
                    gym = check.branch.gym
                    
                    if gym == branch.gym :
                        diagrams = Diagram.objects.filter(branch=branch_id)
                        return Response(DiagramSerialzier(diagrams,many=True).data,status=status.HTTP_200_OK)
                    
                    else:
                        return Response({'error':'user cant access this gym'},status=status.HTTP_400_BAD_REQUEST)
                    
                except Gym_Subscription.DoesNotExist:
                        return Response({'error':'user is not registered in any gym currently'},status=status.HTTP_400_BAD_REQUEST)
                                    
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
        
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
        examples=[]
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


@extend_schema(
        summary='deactivate the expired subscriptions'
    )
@api_view(['GET'])
def check_subscription(request,*args, **kwargs):
    try:
        expired_subs = Gym_Subscription.objects.filter(end_date__lt = now.date(),is_active = True)
        expired_subs.update(is_active=False)
        
        return Response({'success':'SUCCESS'},status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)