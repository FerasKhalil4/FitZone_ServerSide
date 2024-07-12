from collections import defaultdict
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
    # permission_classes = [IsAuthenticated,admin_permissions]
    def get_queryset(self):
        return Gym.objects.filter(is_deleted = False).all()    
    
    def create (self, request, *args, **kwargs):    
        gym_serializer = GymSerializer(data =request.data)        
        if gym_serializer.is_valid(raise_exception=True):
            gym_serializer.save()
            return Response({'data':gym_serializer.data},status=status.HTTP_201_CREATED)
        return Response(gym_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
GymListCreate = GymListCreateAV.as_view()

class GymRetrieveUpdateDestroyAV(generics.RetrieveUpdateDestroyAPIView):
    
    serializer_class = GymSerializer
         
    def get_object(self , pk):
        return Gym.objects.get(pk = pk ,is_deleted = False)       
    
    def get(self, request, pk, *args, **kwargs):
        try:
                gym = self.get_object(pk=pk) or None
                if gym is None:
                    return Response(status=status.HTTP_404_NOT_FOUND)
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
        gym = self.get_object(pk) or None
        if gym is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = GymSerializer(gym ,data = data , partial = True )
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data)
    
    def delete (self ,request, pk, *args , **kwargs):
        gym = self.get_object(pk) or None
        if gym is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            gym.is_deleted = True
            gym.save()
            branches = Branch.objects.filter(gym=gym)
            for branch in branches:
                branch.is_active = False
                branch.save()
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})
        return Response(status=status.HTTP_204_NO_CONTENT)
        
GymRetrieveUpdateDestroy = GymRetrieveUpdateDestroyAV.as_view()   

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
        data['is_trainer'] = False
        data['shift']['branch'] = pk  
        employee_serializer = EmployeeSerializer(data = data)
        if employee_serializer.is_valid(raise_exception=True):
            employee_serializer.save()
        return Response({'data': employee_serializer.data }, status= status.HTTP_201_CREATED)
    
employeeListAV = EmployeeListAV.as_view()

class TrainerListAV(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer
    
    def get_queryset(self, id):
        return Employee.objects.filter(is_trainer = True , user__is_deleted= False , employee__branch_id=id)
    
    def get(self, request, *args, **kwargs):
        try:
            user = request.user 
            employee = Employee.objects.get(user=user)
            branch_id = Shifts.objects.filter(employee=employee).first().branch_id
            qs = self.get_queryset(branch_id)
            serializer = self.get_serializer(qs,many=True)
            return Response(serializer.data)
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})
        
    def post(self, request ,*args , **kwargs):
        data = request.data 
        data['is_trainer'] = True
        employee = Employee.objects.get(user=request.user)
        branch_id = Shifts.objects.filter(employee=employee).first().branch_id
        data['shift']['branch'] = branch_id  
        employee_serializer = EmployeeSerializer(data = data)
        if employee_serializer.is_valid(raise_exception=True):
            employee_serializer.save()
        return Response({'data': employee_serializer.data }, status= status.HTTP_201_CREATED)
    
trainerListAV = TrainerListAV.as_view()

        
class ShiftsCreateAV(generics.CreateAPIView):
    serializer_class = ShiftSerializer
    queryset = Shifts.objects.filter(is_active=True)
    
    def post(self, request, pk, *args, **kwargs):
        data = request.data
        try:
            data['employee'] = pk
            print(data)
            serializer = self.get_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'message':f"shift created Completly",'data' : serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise serializers.ValidationError(str(e))
shiftCreateAV = ShiftsCreateAV.as_view()
        