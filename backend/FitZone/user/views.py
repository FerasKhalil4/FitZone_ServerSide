from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view , extend_schema
from django.contrib.auth.models import User
from rest_framework import status , serializers
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .permissions import ClientCheck
from .DataExample import * 
from disease.serializers import Client_DiseaseSerilaizer
from gym.models import Employee , Shifts , Branch, Gym
from gym.seriailizers import EmployeeSerializer  ,ShiftSerializer 
from gym_sessions.models import Gym_Subscription
from points.models import Points
from wallet.models import Wallet
from wallet.serializers import WalletSerializer
import datetime
from django.db.models import Q
from django.db import transaction
import json

def Check_points_offer():
    check = Points.objects.get(activity = 'First Time Activity')
    if check.points > 0 :
        return check.points
    return 0


def check_validatiy(item):
    if isinstance(item,str):
        try:
            item=json.loads(item)
        except json.JSONDecodeError:
            raise ValueError('invalid format')
        return item
    
class RegistrationAV(generics.CreateAPIView):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    @extend_schema(
        summary='Client Registration',
        examples=registration
    )
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = {}
                
                print(request.data.dict())
                data_ = request.data.dict()
                data_['user_profile'] = check_validatiy(data_['user_profile'])
                data_['diseases'] = check_validatiy(data_['diseases'])
                data_['goal'] = check_validatiy(data_['goal'])
                
                check_offers = Check_points_offer()
                if check_offers != 0:
                    data['points'] = check_offers

                    
                serializer = ClientSerializer(data=data_,context = {'request':request})
                if serializer.is_valid():
                    account = serializer.save()
                    user_profile = serializer.validated_data['user_profile']
                    user_profile.pop('password', None)
                    data['user'] = user_profile
                    
                    print('00000000000000000')
                    goal = data_['goal']
                    client= account['client']
      
                    goal['client'] = client.pk
                    goal_Serializer = GoalSerializer(data=goal)
                    goal_Serializer.is_valid(raise_exception=True)
                    goal_Serializer.save()
                    print('00000000000000000')
                    
                    wallet_data={
                        'client':client.pk,
                    }
                    wallet_serializer = WalletSerializer(data=wallet_data)
                    wallet_serializer.is_valid(raise_exception=True)
                    wallet_serializer.save()
                    diseases = data_.pop('diseases')
                    if len(diseases) != 0:
                        for disease in diseases:
                            disease_ = {
                                'client':client.pk,
                                'disease':disease['id'],
                            }
                            serilaizer = Client_DiseaseSerilaizer(data=disease_)
                            serilaizer.is_valid(raise_exception=True)
                            serilaizer.save()
                        
                    refresh = RefreshToken.for_user(account['user'])
                    data['token'] = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                else:
                    raise ValidationError({
                        'error': 'Please check your data',
                        'error_message': serializer.errors
                    })
                return Response({'data':data,'user_goal':goal_Serializer.data,'message':'you account is created successfully \
                                 please charge you wallet to use the app effectivly'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)},status=status.HTTP_400_BAD_REQUEST)

Registration = RegistrationAV.as_view()

class LoginAV(APIView):
    
    def post(self , request, *args, **kwargs):
        data={}
        account = User.objects.filter(username = request.data.get('username') , is_deleted = False).first()   
        
        if account :
            if account.check_password(request.data.get('password')):
                if account.role == 3 or account.role == 4:
                    try:
                        try:
                            employee = Employee.objects.get(user_id=account.id)
                        except Employee.DoesNotExist:
                            return Response ({'error': 'Account does not exist'},status=status.HTTP_400_BAD_REQUEST)
                        shifts = Shifts.objects.filter(employee=employee, is_active= True)
                        full_time = Shifts.objects.filter(employee=employee, is_active= True,shift_type="FullTime").first() 
                        
                        if full_time is not None:
                            branch_id = full_time.branch_id
                            now = datetime.datetime.now().strftime("%A").lower()
                            days_off = full_time.days_off.values() 

                            if now in days_off:
                                return Response({'error':'you cant login in you days off'},status=status.HTTP_400_BAD_REQUEST)
                            
                        elif shifts: 
                            ids = [shift.branch_id for shift in shifts]
                            branches = Branch.objects.filter(id__in=ids)
                            gym_ids = [branch.gym_id for branch in branches]
                            gyms = Gym.objects.filter(id__in=gym_ids)
                            now = datetime.datetime.now()
                            time_str = now.strftime("%H:%M:%S")
                            current_time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
                            for gym in gyms :
                                current_shift = None
                                if gym.start_hour >= gym.close_hour :

                                    if gym.mid_day_hour >  current_time >= gym.start_hour: 
                                        current_shift = "Morning"
                                    elif gym.mid_day_hour < current_time or current_time < gym.close_hour :
                                        
                                        current_shift = "Night"
                                        
                                elif gym.start_hour < gym.close_hour :
                                    if gym.mid_day_hour >  current_time >= gym.start_hour:
                                         
                                        current_shift = "Morning"
                                    elif gym.mid_day_hour <= current_time < gym.close_hour :
                                        
                                        current_shift = "Night"
                                if current_shift is None:
                                        return Response({'error':'you cant login now, the gym is closed'}, status = status.HTTP_400_BAD_REQUEST)

                                query = Q(employee=employee, shift_type = current_shift, is_active=True) & ~ Q (shift_type = "FullTime" )
                                shift_check = Shifts.objects.filter(query).first()
                                    
                                if shift_check is not None :
                                    now = datetime.datetime.now().strftime("%A").lower()
                                    days_off = shift_check.days_off.values() 

                                    if now in days_off:
                                        return Response({'error':'you cant login in you days off'},status=status.HTTP_400_BAD_REQUEST)
                                    break

                            branch_id = shift_check.branch_id if shift_check is not None else None
                        else:
                            return Response({'message':'You must ne employed to login'} , status=status.HTTP_400_BAD_REQUEST)
                            
                        if branch_id is not None:
                        
                            gym_id = Branch.objects.get(id=branch_id).gym_id  
                            data['branch_id'] = branch_id
                            data['gym_id'] = gym_id
                        else : 
                            return Response({'error':'you cant login now, shift is not allowed'})
                    except Exception as e:
                        raise serializers.ValidationError({'error':str(e)})
                elif account.role == 5:
                    client_current_sub = None
                    try:
                        client = Client.objects.get(user__pk =account.pk)
                        client_current_sub = Gym_Subscription.objects.get(client=client.pk, is_active=True)
                    except Client.DoesNotExist:
                        return Response({'error':'Account does not exist'},status=status.HTTP_400_BAD_REQUEST)
                    except Gym_Subscription.DoesNotExist:
                        pass
                    data['branch_id'] = client_current_sub.branch.pk if client_current_sub is not None else None
                refresh = RefreshToken.for_user(account)
                
                data['token'] = {'refresh_token':str(refresh) ,
                                'access':str(refresh.access_token)} 
                
                data['username'] = account.username  
                data['user_id'] = account.pk
                data['role'] = account.role

                return Response(data, status = status.HTTP_200_OK)
            else:
                return Response({'error':'wrong password'}, status = status.HTTP_403_FORBIDDEN)
        
        return Response({'error':'check on the entered data'}, status = status.HTTP_403_FORBIDDEN)
            
Login = LoginAV.as_view()


class ClientListAV(generics.ListAPIView):
    serializer_class = ClientSerializer
    queryset = Client.objects.filter(user__is_deleted = False)
    
clientListAv = ClientListAV.as_view()
class ClientProfile(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClientSerializer
    queryset = Client.objects.filter(user__is_deleted = False)
    # permission_classes = [ClientCheck]
    
    
    def update(self, request, *args, **kwargs):
        client = self.get_object()
        user_data = request.data.pop('user_profile', None)
        client_serializer = ClientSerializer(client, data=request.data, partial=True)
        
        if user_data:
            user = client.user
            user_serializer = UserSerializer(user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        
        client_serializer.is_valid(raise_exception=True)
        client_serializer.save()
        
        return Response( client_serializer.data)
client_profile = ClientProfile.as_view()



class EmployeeDetailAV(generics.RetrieveUpdateDestroyAPIView):
    
    serializer_class = EmployeeSerializer  
    
    def get_object(self):
        pk = self.kwargs['pk']
        return get_object_or_404(Employee , pk = pk , user__is_deleted=False)

    @extend_schema(
        description=" Retrieve the details of the employee with their associated user and shift information.",
    )
    def get(self, request, *args, **kwargs):
        try:
            instance = Employee.objects.get(pk = kwargs.get('pk') , user__is_deleted = False)
        except :
            raise serializers.ValidationError({'error':'user does not exist'})
        employee_serializer = self.get_serializer(instance)
        user_serializer = UserSerializer(instance.user)
        shifts = Shifts.objects.filter(employee=instance)
        shift_serializer = ShiftSerializer(shifts, many=True)

        data = {
            "employee_data": employee_serializer.data,
            "user_data": user_serializer.data,
            "shift_serializer": shift_serializer.data
        }

        return Response(data)
    
    @extend_schema(
        summary="Retrieve Employee Details",
        description="Retrieve the details of the employee with their associated user and shift information."
   )
    def put(self ,request, *args, **kwargs ):
     
        instance = self.get_object()
        user_data = request.data.pop('user_data',None)
        employee_serializer = self.get_serializer(data = request.data , instance = instance , partial = True)
        if employee_serializer.is_valid(raise_exception=True):
            employee_serializer.save()
        if user_data is not None:
            user_serializer =UserSerializer( instance.user, data = user_data , partial = True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.validated_data.pop('role',None)
            user_serializer.save()
        return Response({
                    "employee_data": employee_serializer.data,
                    "user_data": user_serializer.data
                })
        
        # delete the employee by their managers
    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        shifts = Shifts.objects.filter(employee=employee)
        for shift in shifts:
            shift.is_active = False
            shift.save()
           
        employee.user.is_deleted = True
        employee.user.save()
        
        return Response(status= status.HTTP_204_NO_CONTENT)
        
        
employeeDetailAV = EmployeeDetailAV.as_view()

class GoalListAV(generics.CreateAPIView):
    serializer_class = GoalSerializer
    queryset = Goal.objects.filter(is_deleted=False)
    def post(self, request, pk, *args, **kwargs):
        data = request.data
        try:
            client = Client.objects.get(user = request.user.id)
            data['client']=client.id
            
            serializer = GoalSerializer(data = data, context = {'request': request,'client': client})
            height = client.height / 100
            data['current_BMI'] = data['weight'] / pow(height, 2)
            if serializer.is_valid(raise_exception=True):                
                serializer.save()
                return Response(serializer.data, status= status.HTTP_201_CREATED)
        except Exception as e:
            raise serializers.ValidationError(str(e))
            
GoalListAv = GoalListAV.as_view()
class GoalDetailDetailsAV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalSerializer
    queryset = Goal.objects.filter(is_deleted=False)
    
    def put(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data=request.data
                instance=self.get_object()
                serializer = self.get_serializer(instance, data=data,partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':'goal is updated successfully'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
GoalDetailDetails = GoalDetailDetailsAV.as_view()

    
@extend_schema(
    summary='client Profilte shown to the employee'
)
class CLientProfileEmployeeListAV(generics.ListAPIView):
    serializer_class = ClientSerializer
    queryset = Client.objects.filter(user__is_deleted=False)
    
    def get(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(pk =kwargs.get('client_id'))
            serializer = self.get_serializer(client).data 
            gender = 'male' if serializer['user']['gender'] == True else 'female'
            
            data = {
                'pk':serializer['id'],
                'username':serializer['user']['username'],
                'birth_date':serializer['user']['birth_date'],
                'age':serializer['user']['age'],
                'address':serializer['address'],
                'height':serializer['height'],
                'gender' : gender, 
                "image_path":serializer['image_path'],
            }
            return Response(data, status=status.HTTP_200_OK)        
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)
employeeClientCheck = CLientProfileEmployeeListAV.as_view()
