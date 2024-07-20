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
from gym.models import Employee , Shifts , Branch, Gym
from gym.seriailizers import EmployeeSerializer  ,ShiftSerializer 
import datetime
from django.db.models import Q

class RegistrationAV(APIView):
    def post(self, request, *args, **kwargs):
        data = {}
        serializer = ClientSerializer(data=request.data)
        
        if serializer.is_valid():
            account = serializer.save()
            user_profile = serializer.validated_data['user_profile']
            user_profile.pop('password', None)
            data['user'] = user_profile
            
            # if user_profile['role'] == 3 or user_profile['role'] == 4:
            #     employee = Employee.objects.get(user_id=user_profile['id'])
            #     branch_id = Shifts.objects.get(employee=employee, is_active= True).branch_id
            #     gym_id = Branch.objects.get(id=branch_id).gym_id
            #     data['branch_id'] = branch_id
            #     data['gym_id'] = gym_id
                #do the same for client
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
        return Response(data, status=status.HTTP_201_CREATED)

Registration = RegistrationAV.as_view()

class LoginAV(APIView):
    
    def post(self , request, *args, **kwargs):
        data={}
        account = User.objects.filter(username = request.data.get('username') , is_deleted = False) .first()   
        
        if account :
            if account.check_password(request.data.get('password')):
                if account.role == 3 or account.role == 4:
                    try:
                        employee = Employee.objects.get(user_id=account.id)
                        shifts = Shifts.objects.filter(employee=employee, is_active= True)
                        full_time = Shifts.objects.filter(employee=employee, is_active= True,shift_type="FullTime") 
                        
                        if full_time.exists():
                            branch_id = full_time.branch_id
                        else : 
                            ids = [shift.branch_id for shift in shifts]
                            branches = Branch.objects.filter(id__in=ids)
                            gym_ids = [branch.gym_id for branch in branches]
                            gyms = Gym.objects.filter(id__in=gym_ids)
                            mid_day_hours = [gym.mid_day_hour for gym in gyms]
                            now = datetime.datetime.now()
                            time_str = now.strftime("%H:%M:%S")
                            current_time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
                            
                            for gym in gyms :
                                
                                if gym.start_hour > gym.close_hour :
                                    if gym.mid_day_hour >  current_time >= gym.start_hour: 
                                        current_shift = "Morning"
                                    elif gym.mid_day_hour < current_time or current_time < gym.close_hour :
                                        current_shift = "Night"
                                        
                                elif gym.start_hour < gym.close_hour :
                                    
                                    if gym.mid_day_hour >  current_time >= gym.start_hour: 
                                        current_shift = "Morning"
                                    elif gym.mid_day_hour <= current_time < gym.close_hour :
                                        current_shift = "Night"
                                    
                                query = Q(employee=employee, shift_type = current_shift, is_active=True) & ~ Q (shift_type = "FullTime" )
                                shift_check = Shifts.objects.get(query) or None
                                if shift_check is not None :
                                    break
                                
                            print(shift_check)
                            branch_id = shift_check.branch_id if shift_check else None
                            
                        if branch_id is not None:
                        
                            gym_id = Branch.objects.get(id=branch_id).gym_id  
                            data['branch_id'] = branch_id
                            data['gym_id'] = gym_id
                        else : 
                            return Response({'error':'you cant login check on this date as an employee'})
                    except Exception as e:
                        raise serializers.ValidationError({'error':str(e)})
                refresh = RefreshToken.for_user(account)
                
                data['token'] = {'refresh_token':str(refresh) ,
                                'access':str(refresh.access_token)} 
                
                data['username'] = account.username  
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
    queryset = Goal.objects.all()
    def post(self, request, pk, *args, **kwargs):
        data = request.data
        try:
            client = Client.objects.get(user = request.user.id)
            data['client']=client.id
            
            serializer = GoalSerializer(data = data, context = {'request': request,'client': client})
            data['current_BMI'] = data['weight'] / pow(client.height, 2)
            if serializer.is_valid(raise_exception=True):                
                serializer.save()
                return Response(serializer.data, status= status.HTTP_201_CREATED)
        except Exception as e:
            raise serializers.ValidationError(str(e))
            
GoalListAv = GoalListAV.as_view()

