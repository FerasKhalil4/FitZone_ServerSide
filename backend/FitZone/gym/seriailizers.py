from rest_framework import serializers
from user.serializers import UserSerializer
from user.models import User
from .models import *
from django.db.models import Q, F
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse    


def create_qr_code_for_branch(request, validated_data,gym):
        base_url = get_current_site(request)
        branch = Branch.objects.create(gym=gym,**validated_data)
        url = f"http://{base_url}{reverse('check_session', args=[str(branch.pk)])}"
        branch.url = url
        branch.save()
        return branch
    
    
class Registration_FeeSerializer(serializers.ModelSerializer):
    fee_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    class Meta:
        model = Registration_Fee
        fields=['gym','fee','type','fee_id']
    
    
class BranchSerializer(serializers.ModelSerializer):
    address = serializers.CharField(max_length=50)
    class Meta :
        model = Branch
        fields = ['id','address' ,'city','street', 'has_store' , 'is_active','qr_code_image','url','number_of_clients_allowed','current_number_of_clients']
        
    def create(self, validated_data):
        request = self.context.get('request')
        print(validated_data)
        gym = validated_data.pop('gym', None)
        return create_qr_code_for_branch(request, validated_data,gym)

class WomanHoursSerializer(serializers.ModelSerializer):
    start_hour = serializers.TimeField(format="%H:%M:%S")
    end_hour = serializers.TimeField(format="%H:%M:%S")
    
    class Meta:
        model = Woman_Training_Hours
        
        fields = ['id','start_hour','end_hour','day_of_week']
        
    def validate(self ,data):

        if data.get('start_hour') > data.get('end_hour') :
            raise serializers.ValidationError('Start time should be less than end time')
        return data
    
    def create(self, validated_data):
        gym = validated_data.pop('gym', None)       
        start_hour = validated_data.get('start_hour')
        end_hour = validated_data.get('end_hour')
        
        if gym.start_hour > gym.close_hour:
            if not ((gym.start_hour <= start_hour or start_hour < gym.close_hour) and
                    (gym.start_hour < end_hour or end_hour <= gym.close_hour)):
                raise serializers.ValidationError('check on the women scedule')
            
        elif gym.close_hour > gym.start_hour: 
                if not( gym.start_hour <= start_hour < gym.close_hour and \
                    gym.start_hour < start_hour <= gym.close_hour):
                    raise serializers.ValidationError('check on the women scedule')
        try:
            day = Woman_Training_Hours.objects.create(gym=gym, **validated_data)
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})     
        
        return day
        
        
class GymSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(write_only=True , required=True)
    manager_details = UserSerializer(write_only=True , required = False)
    manager = UserSerializer(read_only=True)
    woman_gym = WomanHoursSerializer(read_only=True, many = True, required=False)
    woman_hours = WomanHoursSerializer(many=True,write_only=True , required=False)
    manager_id = serializers.IntegerField(write_only= True , required = False)
    start_hour = serializers.TimeField(input_formats=["%H:%M:%S"])
    close_hour = serializers.TimeField(input_formats=["%H:%M:%S"])
    mid_day_hour = serializers.TimeField(input_formats=["%H:%M:%S"])
    created_at = serializers.DateTimeField(read_only=True)
    allow_retrival = serializers.BooleanField(write_only=True)
    duration_allowed = serializers.IntegerField(write_only=True , required = False)
    cut_percentage = serializers.FloatField(write_only=True ,required = False)
    fees = Registration_FeeSerializer(read_only=True,many=True)
    branch_data = BranchSerializer(source='gym',read_only=True,many=True)
    
    class Meta:
        model = Gym
        fields =['id','allow_public_posts','allow_public_posts','name' , 'description','image_path',
                 'created_at','start_hour','close_hour' ,'mid_day_hour','manager',
                 'manager_id','manager_details','branch','woman_gym','woman_hours','allow_branches_access','branch_data',
                 'allow_retrival', 'duration_allowed', 'cut_percentage','fees','allowed_days_for_registraiton_cancellation']   
        
        
    def validate(self ,data):
        if data.get('allow_retrival') == True and (not data.get('duration_allowed') or not data.get('cut_percentage')):
             raise serializers.ValidationError({'error':'please provide the complete data about the dutation and the percentage cut'})
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if not validated_data.get('manager_details') and not validated_data.get('manager_id') :
            raise serializers.ValidationError({'error':'please provide the manager_id or the data to create manger '})
        branch_data = validated_data.pop('branch',None)
        manager_data = validated_data.pop('manager_details',None)
        manager_id = validated_data.pop('manager_id' , None)
        woman_hours = validated_data.pop('woman_hours',[])

        woman_serializer = WomanHoursSerializer(data = woman_hours )
        
        if manager_id is not None:
            try:
                manager = User.objects.get(pk = manager_id) or None
            except:
                raise serializers.ValidationError({'error':'manager not found'})            
        else:   
            manager_data['role'] = 2        
            manager_serializer = UserSerializer(data = manager_data)
            if manager_serializer.is_valid():
                manager = manager_serializer.save()
            else:            
                raise serializers.ValidationError(manager_serializer.errors)
        
        gym = Gym.objects.create(manager = manager ,**validated_data)
        
        woman_hours_instances = []
        
        branch = create_qr_code_for_branch(request, branch_data,gym)

        for woman_hour in woman_hours:   
            woman_serializer = WomanHoursSerializer(data=woman_hour)
            woman_serializer.is_valid(raise_exception=True)
            woman_serializer.save(gym = gym)
            woman_hours_instances.append(woman_hours_instances) 
        return gym
    
    
class EmployeeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    user = UserSerializer(required=False)
    user_id = serializers.PrimaryKeyRelatedField(source = 'user', 
                                                 queryset = User.objects.filter(is_deleted=False) , write_only=True,required=False)
    class Meta:
        model = Employee
        fields = ['id','is_trainer','user','user_id']
    
    def create(self, data):
        try:
            print(data)
            user = data.get('user', None)
            user_id = None
            if isinstance(user,User):
                user_id = user.id
            
            if user_id is not None:
                user = User.objects.get(id = user_id) or None
                
                if user is not None:
                    employee = Employee.objects.get(id = user_id)
                    
            else:
                user_data = data.pop('user',None)
                if user_data is not None :
                    if data['is_trainer'] == False:
                        user_data['role'] = 3
                    else:
                        user_data['role'] = 4
                    user_serializer = UserSerializer(data = user_data)
                    user_serializer.is_valid(raise_exception=True)
                    user = user_serializer.save()
                
                employee = Employee.objects.create(user = user,  **data)

            return employee
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})
        
class ShiftSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.filter(is_active=True), write_only=True, required=True)
    branch_details = BranchSerializer(source='branch', read_only=True)
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(source = 'employee',
                                                    queryset=Employee.objects.filter(user__is_deleted=False), 
                                                    write_only=True)
    class Meta:
        model = Shifts
        fields = [ 'shift_type','employee' ,'employee_id', 'id', 'branch', 'branch_details', 'is_active', 'days_off']
    
    days_of_week = {
    1: 'sunday',
    2: 'monday',
    3: 'tuesday',
    4: 'wednesday',
    5: 'thursday',
    6: 'friday',
    7: 'saturday'
}
    def validate(self, data):
        if data.get('shift_type') not in ['FullTime','Morning','Night']:
            raise serializers.ValidationError('shift type should be FullTime, Morning or Night')
        query = (Q(employee = data.get('employee')) 
                 & (Q(shift_type = data.get('shift_type'))
                  | Q(shift_type ='FullTime')))
        check_overlap_shift = Shifts.objects.filter(query)
        if check_overlap_shift.exists():
            raise serializers.ValidationError('there is an overlap, check on the employee shift scheduel')
        return data
    
    def validate_days_off(self,data):
      
        days = list(data.values())
        if len(days) != len(set(days)):
            raise serializers.ValidationError({"error":"please check on the days entered"})
        
        for day in data.values():
            if day not in self.days_of_week.values():
                raise serializers.ValidationError(f'{day} is not a valid day of the week')
        data= {day:day_name for day, day_name in self.days_of_week.items() if day_name in data.values() }
            
        return data

    def create(self, validated_data):
        employee_id = validated_data.pop('employee')
        shift = Shifts.objects.create(**validated_data, employee=employee_id)
        return shift   

class TrainerSerialzier(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(source = "employee",
                                                     queryset=Employee.objects.filter(user__is_deleted=False)
                                                     ,write_only=True)
    employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = Trainer 
        fields= ['id','employee','employee_id','allow_public_posts','online_training_price','private_training_price']

class AvailableGymsSerializer(serializers.ModelSerializer):
    branches = serializers.SerializerMethodField()
    fees = Registration_FeeSerializer(read_only=True,many=True)
    woman_gym = WomanHoursSerializer(read_only=True, many = True, required=False)
    
    class Meta:
        model = Gym
        fields = ['name','description','image_path','branches','start_hour','close_hour','fees','woman_gym',]

    def get_branches(self, obj):
        return BranchSerializer(Branch.objects.filter(
            gym=obj,
            is_active=True,
            number_of_clients_allowed__gt=F('current_number_of_clients')
        ),many=True).data
