import traceback
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView 
from rest_framework import generics , status
from user.serializers import UserSerializer
from .seriailizers import *
from .models import Gym, Branch , Employee
from .permissions import admin_permissions  , Manager_permissions
from rest_framework.permissions import IsAuthenticated

class GymListCreateAV(generics.ListCreateAPIView):
    serializer_class = GymSerializer
    permission_classes = [IsAuthenticated,admin_permissions]
    def get_queryset(self):
        return Gym.objects.filter(is_deleted = False).all()    
    
    
    def create (self, request, *args, **kwargs):    
        gym_serializer = GymSerializer(data =request.data)        
        if gym_serializer.is_valid(raise_exception=True):
            gym_serializer.save()
            return Response({'data':gym_serializer.data},status=201)
        return Response(gym_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
GymListCreate = GymListCreateAV.as_view()

class GymRetrieveDestroyAV(generics.RetrieveDestroyAPIView):
    
    serializer_class = GymSerializer
    
    def get_queryset(self):
        return Gym.objects.filter(is_deleted = False).all()       
    def get_object(self , pk):
        return Gym.objects.filter(pk = pk , is_deleted = False).get()         
    
    def get(self, request, pk, *args, **kwargs):
        try:
                gym = Gym.objects.filter(pk=pk).get()
                branches = Branch.objects.filter(gym=gym)
                branches_data = {
                'data': BranchSerializer(branches, many=True).data,
                'gym': GymSerializer(gym).data
                }
                return Response(branches_data)
        except Gym.DoesNotExist:
            return Response(status=404)
    
    def update(self ,request, pk, *args , **kwargs):
        data = request.data 
        gym = self.get_object(pk)
        serializer = GymSerializer(gym ,data = data , partial = True )
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data)
GymRetrieveDestroy = GymRetrieveDestroyAV.as_view()   

class ManagerGymListAV(generics.ListAPIView):
    serializer_class = GymSerializer
    
    def get_queryset(self):
        return Gym.objects.filter(is_deleted=False).all()
    
    
    def get(self, request, *args, **kwargs):
        try:
            manager = request.user 
            gyms = Gym.objects.filter(manager=manager)
            gym_data = {
                'gyms_data':GymSerializer(gyms , many=True).data
            }
            return Response(gym_data , status = 200)
        except Exception as e:
            print(f"Exception occurred: {type(e).__name__}")
        
            return Response({"error": "An error occurred while fetching the gym data."}, status=500)
managergymAV = ManagerGymListAV.as_view()

class BracnchAV(generics.ListCreateAPIView):
    serializer_class = BranchSerializer 
    queryset = Branch.objects.all()
    
    def get(self , request , pk , *args , **kwargs):
        branches_data = {}
        try:
            gym = Gym.objects.filter(id=pk).get()
            branches = Branch.objects.filter(gym=gym)
            branches_data = {
                'data': BranchSerializer(branches, many=True).data,
                'gym': GymSerializer(gym).data
            }
            return Response(branches_data)
                
        except Gym.DoesNotExist:
            return Response({'error':'check on the gym id entered'},status=404)
        
    def create(self , request , pk , *args , **kwargs):
        gym = Gym.objects.get(id=pk)
        data = request.data 
        serializer = BranchSerializer(data = data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(gym=gym)
            return Response(serializer.data)
                
branchAv = BracnchAV.as_view()

class BranchDetailAV(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [Manager_permissions]
    
    def update(self, request, pk, *args , **kwargs):
        try:
            data = request.data 
            branch = Branch.objects.get(pk = pk)            
            serializer = BranchSerializer(branch , data=data, partial=True)
            print(serializer.is_valid())
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            return Response({'error':'please check on the provided args' , 'exception':str(e)} , status=400)

branchDetailAV =BranchDetailAV.as_view()

class EmployeeListAV(generics.ListCreateAPIView):  
    queryset = Employee.objects.all()
    serializer_class = ShiftSerializer  
    # permission_classes = []
    def get(self, request, pk, format=None):
        
        shifts = Shifts.objects.filter(branch_id=pk)
        shift_serializer = ShiftSerializer(shifts , many = True)
        shift_data = shift_serializer.data        
        employee_ids = {shift['employee'] for shift in shift_data}
        emps = {}
        
        for id in employee_ids:
            emp = Employee.objects.get(id=id)
            emp_serializer = EmployeeSerializer(emp)
            emps[id] = emp_serializer.data
            
        for shift in shift_data:
            shift['employee'] = emps[shift['employee']]
            
        return Response(shift_data)
        
   
    def post(self, request, pk ,*args , **kwargs):
        data = request.data 
        data['shift']['branch'] = pk  
        employee_serializer = EmployeeSerializer(data = data)
        if employee_serializer.is_valid(raise_exception=True):
            employee_serializer.save()
        return Response({'data': employee_serializer.data  }, status= status.HTTP_201_CREATED)
    
employeeListAV = EmployeeListAV.as_view()



        
# {	"name":"gym_32",	"description":"description_23",	"regestration_price":9.99,	"allow_retrival":false,	"start_hour":"09:00:00",	"close_hour":"00:00:00"	}