from collections import defaultdict
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView 
from rest_framework import generics , status
from user.serializers import UserSerializer
from .seriailizers import *
from .models import Gym, Branch , Employee
from .permissions import admin_permissions  , Manager_permissions, admin_manager_permissions
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from community.paginations import Pagination
class GymListCreateAV(generics.ListCreateAPIView):
    serializer_class = GymSerializer
    pagination_class = Pagination
    # permission_classes = [IsAuthenticated,admin_permissions]
    
    def get_queryset(self):
        return Gym.objects.filter(is_deleted = False).all()    
    @transaction.atomic
    def post (self, request, *args, **kwargs): 
        registration_fee = request.data.pop('registration_fee') 
        type_check = {data['type'] for data in registration_fee}
        try:  
            if len(registration_fee) != len(type_check):
                return Response({"message":"there is redundant data in the fee data"})
            gym_serializer = GymSerializer(data =request.data)        
            if gym_serializer.is_valid(raise_exception=True):
                gym = gym_serializer.save()
                fee_details = []
                for fee in registration_fee :      
                    fee['gym'] = gym.id
                    fee_serializer = Registration_FeeSerializer(data=fee)
                    if fee_serializer.is_valid(raise_exception=True):
                        fee_serializer.save()
                        fee_details.append(fee_serializer.data)
                return Response({'data':gym_serializer.data, 'fee':fee_details},status=status.HTTP_201_CREATED)
            return Response(gym_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e :
            return Response({'error': str(e)})
        
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
        
        registration_fee = request.data.get('registration_fee',None)
        if registration_fee is not None:
            for fee in registration_fee:
                try:
                    fee_ = Registration_Fee.objects.get(gym=gym,type=fee['type']) 
                except Registration_Fee.DoesNotExist:
                    fee_ = None
                    
                if fee_ is None:    
                    fee['gym'] = gym.pk
                    fee_serializer = Registration_FeeSerializer(data=fee)
                    if fee_serializer.is_valid(raise_exception=True):
                        fee_serializer.save()
                else:
                    fee_serializer = Registration_FeeSerializer(instance=fee_, data=fee,partial=True)
                    if fee_serializer.is_valid(raise_exception=True):
                        fee_serializer.save()
            
        if gym is None:
            return   Response(status=status.HTTP_404_NOT_FOUND)
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
            return Response({"error": str(e)}, status=500)
managergymAV = ManagerGymListAV.as_view()

class BracnchAV(generics.ListCreateAPIView):
    serializer_class = BranchSerializer 
    queryset = Branch.objects.all()
    permission_classes = [admin_manager_permissions]
    
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
            return Response({'message':"Branch Created successfully",
                             "data":serializer.data})
                
branchAv = BracnchAV.as_view()

class BranchDetailAV(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [admin_manager_permissions]
    
    def update(self, request, pk, *args , **kwargs):
        try:
            data = request.data 
            branch = Branch.objects.get(pk = pk)            
            serializer = BranchSerializer(branch , data=data, partial=True)
            print(serializer.is_valid())
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message':"Branch Updated Successfully",'data':serializer.data})
        except Exception as e:
            return Response({'error':'please check on the provided args' , 'exception':str(e)} , status=400)

branchDetailAV =BranchDetailAV.as_view()

class EmployeeListAV(generics.ListCreateAPIView):  
    queryset = Employee.objects.all()
    serializer_class = ShiftSerializer  
    # permission_classes = []
    def get(self, request, branch_id, format=None):
        try:
            shifts = Shifts.objects.filter(branch_id=branch_id)
            shift_serializer = ShiftSerializer(shifts , many = True)
            shift_data = shift_serializer.data                     
            return Response(shift_data)
        except Exception as e :
            return Response ({'error': str(e)})
    def post(self, request, branch_id ,*args , **kwargs):
        try:
            with transaction.atomic():
                data = request.data 
                data['is_trainer'] = False
                data['shift']['branch'] = branch_id  
                employee_serializer = EmployeeSerializer(data = data)
                employee_serializer.is_valid(raise_exception=True)
                employee = employee_serializer.save()
                shift = data.pop('shift' , None)
                if shift is not None:
                    shift['employee_id'] = employee.id
                    shift['branch'] = shift['branch']
                    shift_serializer = ShiftSerializer(data = shift)
                    shift_serializer.is_valid(raise_exception=True)
                    shift = shift_serializer.save()
                return Response({'message':'employee created successfully',
                    'data': employee_serializer.data }, status= status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error':'please check on the provided args', 'exception':str(e)}, status=400)
    
employeeListAV = EmployeeListAV.as_view()

class TrainerListAV(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer
    
    def get_queryset(self, id):
        return Employee.objects.filter(is_trainer = True , user__is_deleted= False , employee__branch_id=id)

    def get(self, request,branch_id, *args, **kwargs):
        try:
            qs = self.get_queryset(branch_id)
            serializer = self.get_serializer(qs,many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)})

    def post(self, request ,branch_id,*args , **kwargs):
        try:    
            with transaction.atomic():
                data = request.data 
                data['is_trainer'] = True

                data['shift']['branch'] = branch_id
                
                employee_serializer = EmployeeSerializer(data = data)
                if employee_serializer.is_valid(raise_exception=True):
                    employee = employee_serializer.save()
                trainer_data = data.pop('trainer_data',None)
                
                trainer_data['employee_id'] = employee.pk
                trainer_Serializer = TrainerSerialzier(data=trainer_data)
                trainer_Serializer.is_valid(raise_exception=True)
                trainer_Serializer.save()
                
                shift = data.pop('shift' , None)
                
                if shift is not None:
                    
                    shift['employee_id'] = employee.id
                    shift['branch'] = shift['branch']
                    
                    shift_serializer = ShiftSerializer(data = shift)
                    shift_serializer.is_valid(raise_exception=True)
                    shift = shift_serializer.save()
                    
                return Response({'message':"Trainer Created Successfully",
                            'data': employee_serializer.data }, status= status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message':str(e)} , status=status.HTTP_400_BAD_REQUEST)
    
trainerListAV = TrainerListAV.as_view()

        
class ShiftsCreateAV(generics.CreateAPIView):
    serializer_class = ShiftSerializer
    queryset = Shifts.objects.filter(is_active=True)
    
    def post(self, request, pk, *args, **kwargs):
        data = request.data
        try:
            data['employee'] = pk
            serializer = self.get_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                if data.get('shift_type')=="FullTime":
                    shifts = Shifts.objects.filter(employee=pk,is_active=True) or None
                    if shifts is not None:
                        for shift in shifts:
                            shift.is_active = False
                            shift.save()
                serializer.save()
                return Response({'message':"shift created Completly",'data' : serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)})

shiftCreateAV = ShiftsCreateAV.as_view()

class ShiftsUpdateAV(generics.RetrieveAPIView):
    serializer_class = ShiftSerializer
    queryset = Shifts.objects.filter(is_active=True)
    #manager
    def put(self, request, pk, *args, **kwargs):
        try:
            shift_ = Shifts.objects.get(pk=pk)
            data = request.data 
            if data.get('shift_type')=="FullTime":
                shifts = Shifts.objects.filter(employee=shift_.employee_id,is_active=True).exclude(pk=pk)
                for shift in shifts:
                    shift.is_active = False
                    shift.save()
            serializer = ShiftSerializer(shift_, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save() 
            return Response({'message': 'Shift updated successfully','data': serializer.data}, status=status.HTTP_200_OK)
        except Shifts.DoesNotExist:
            return Response({'error': 'Shift does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            raise serializers.ValidationError(str(e))
shiftUpdateAV = ShiftsUpdateAV.as_view()

class Registration_feeListAV(generics.ListAPIView):
    serializer_class = Registration_FeeSerializer
    
    def get_queryset(self):
        return Registration_Fee.objects.filter(gym_id=self.kwargs['gym_id'])
    
fee_list = Registration_feeListAV.as_view()