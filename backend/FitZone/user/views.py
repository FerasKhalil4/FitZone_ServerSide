from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view , extend_schema
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, ClientSerializer
from .models import Client
from .permissions import ClientCheck
from gym.models import Employee , Shifts , Branch
from gym.seriailizers import EmployeeSerializer , BranchSerializer ,ShiftSerializer

class RegistrationAV(APIView):
    # @extend_schema(
    #     operation_id='custom_operation_id',
    #     summary='My custom view',
    #     description='Detailed description of my view.',
    # )
    def post(self, request, *args, **kwargs):
        data = {}
        serializer = ClientSerializer(data=request.data)
        
        if serializer.is_valid():
            account = serializer.save()
            
            user_profile = serializer.validated_data['user_profile']
            user_profile.pop('password', None)
            data['user'] = user_profile

            refresh = RefreshToken.for_user(account)
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
        print(request.data)
        account = User.objects.filter(username = request.data.get('username') , is_deleted = False) .first()   
        
        if account :
            if account.check_password(request.data.get('password')):
                    refresh = RefreshToken.for_user(account)
                    return Response({'token':{'refresh_token':str(refresh) ,
                                              'access':str(refresh.access_token)} , 
                                     'username' :account.username                                      
                                         }, status = 200)
            else:
                return Response({'error':'wrong password'}, status = 403)
        
        return Response({'error':'check on the entered data'}, status = 403)
            
Login = LoginAV.as_view()

class ClientProfile(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClientSerializer
    permission_classes = [ClientCheck]

    def get_object(self):
            return self.request.user.client
    
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

class EmployeeDetailAV(generics.RetrieveAPIView):
    
    serializer_class = EmployeeSerializer  
    
    def get_object(self):
        pk = self.kwargs['pk']
        return get_object_or_404(Employee , pk = pk , user__is_deleted=False)

    @extend_schema(
        description=" Retrieve the details of the employee with their associated user and shift information.",
    )
    def get(self, request, *args, **kwargs):
        """
        This endpoint returns the following data:
        - Employee fields (e.g. start_data , is_trainer ..)
        - User fields (e.g. email, username ..)
        - Shift details (e.g. shift_type, is_active..)
        
        Parameters:
        - the id given is the id of the employee
        
        Returns:
        - A JSON object containing the employee, user, and shift details.
        """
        instance = Employee.objects.get(pk = kwargs.get('pk') , user__is_deleted = False)
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
        """
        -employee updating his profile data
        
        This endpoint returns the following data:
        - Employee fields (e.g. start_data , is_trainer ..)
        - User fields (e.g. email, username ..)
        
        Parameters:
        - the id given is the id of the employee
        
        Returns:
        - A JSON object containing basic employee, user data.
        """
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
