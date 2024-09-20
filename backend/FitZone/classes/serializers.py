from rest_framework import serializers 
from .models import *
from .services import RegistrationClassService,UpdateRegistrationService
from gym.seriailizers import TrainerSerialzier, BranchSerializer
from gym.models import Trainer ,Gym , Branch
from django.db.models import Q
import datetime 
from dateutil.relativedelta import relativedelta

class Class_ScheduelSerializer(serializers.ModelSerializer):
    class_scheduel_id = serializers.PrimaryKeyRelatedField(source = 'id',read_only = True)
    trainer = TrainerSerialzier(read_only=True)
    trainer_id = serializers.PrimaryKeyRelatedField(source = 'trainer',
        queryset=Trainer.objects.filter(employee__user__is_deleted=False),
        write_only=True)

    class Meta:
        model = Class_Scheduel
        fields=['start_date','end_date','start_time','end_time','trainer','trainer_id','days_of_week'
                ,'class_scheduel_id','hall','allowed_number_for_class','allowed_days_to_cancel','current_number_of_trainees']
        
        
    def validate(self, data):
        days_of_week = {
            1: 'sunday',
            2: 'monday',
            3: 'tuesday',
            4: 'wednesday',
            5: 'thursday',
            6: 'friday',
            7: 'saturday'
        }
        
        def get_used_data(days):
            return {str(day):day_name for day, day_name in days_of_week.items() if day_name in days.values()}
        
        def validate_days(days):
            if days is None : 
                raise serializers.ValidationError({'error':'please add the days of the class'})
            if len(days) != len(set(days)):
                raise serializers.ValidationError({"error": "please check on the days entered"})
            for day in days:
                if day not in days_of_week.values():
                    raise serializers.ValidationError({"error": "please check on the days entered"})
        
        def get_gym_details(branch_id):
            try:
                gym_id = Branch.objects.get(id=branch_id).gym_id
                return Gym.objects.get(id=gym_id)
            except Exception as e:
                raise serializers.ValidationError({'error': str(e)})
        
        def check_time_validity(gym, start_time, end_time):
            try:
                if gym.start_hour > gym.close_hour:
                    if (gym.start_hour <= start_time or start_time < gym.close_hour) and \
                    (gym.start_hour < end_time or end_time <= gym.close_hour):
                        return True
                    else:
                        raise serializers.ValidationError({'error': 'Please check the schedule of the gym and the entered class data'})
                
                elif gym.start_hour < gym.close_hour:
                    if gym.start_hour <= start_time < gym.close_hour and \
                    gym.start_hour < end_time <= gym.close_hour:
                        return True
                    else:
                        raise serializers.ValidationError({'error': 'Please check the schedule of the gym and the entered class data'})
            except Exception as e:
                raise serializers.ValidationError(str(e))
            
        def check_date_validity(start_date, end_date):
            if start_date <= datetime.date.today():
                raise serializers.ValidationError('Start date should be greater than or equal to today.')
            if end_date <= start_date:
                raise serializers.ValidationError('End date should be greater than start date.')
            
        def days_of_week_overlap(value):

            query = Q()
            for day , day_name in value.items():
                query |= Q(scheduel__days_of_week__contains= {day:day_name})
            return query

        def check_overlap(data, used_data):
            trainer = data['trainer']
            trainer_id = trainer.pk
            overlap_con = (
                Q(
                 scheduel__hall = data['hall'],
                 scheduel__start_date__lte = data['start_date'],
                 scheduel__end_date__gt = data['start_date'],
            )
            )|(
                Q(
                 scheduel__start_date__lt = data['end_date'],
                 scheduel__end_date__gte = data['end_date'],
                  scheduel__hall=data['hall'],
            )
            )|(
                Q(
                 scheduel__hall = data['hall'],
                 scheduel__start_date__gte = data['start_date'],
                 scheduel__end_date__lte = data['end_date'],
            )
            )
            
            overlap_con &= (Q( scheduel__start_time__lte = data['start_time'],  scheduel__end_time__gt = data['start_time'])
                 | Q( scheduel__start_time__lt = data['end_time'],  scheduel__end_time__gte = data['end_time'])
                 | Q( scheduel__start_time__gte = data['start_time'],  scheduel__end_time__lte = data['end_time'])
                 )
            overlap_con &= days_of_week_overlap(used_data)
            overlap_con &= (Q(
                    scheduel__trainer = trainer_id
                ) | ~Q (
                     scheduel__trainer = trainer_id
                )
              )
            
            instance_ = self.context.get('instance') or None
            if instance_ is not None:
                instance = instance_.id
                overlap_con &= ~Q(id=instance) 
            overlapped_classed = Classes.objects.filter(overlap_con)
            if overlapped_classed.exists():
                raise serializers.ValidationError('This class overlaps with another one in the same hall and date range.')

        days = list(data.get('days_of_week').values())
        
        if data['allowed_number_for_class'] < 0 :
            raise serializers.ValidationError({"error": "please check on the allowed_number_for_class  must be a positive value"})
        
        used_data = get_used_data(data['days_of_week'])
        
        request = self.context.get('request')
        user = request.user
        branch_id = self.context.get('branch_id')
        gym = get_gym_details(branch_id)        
        check_time_validity(gym, data['start_time'], data['end_time'])
        check_date_validity(data['start_date'], data['end_date'])
        check_overlap(data, used_data)
        
        data['days_of_week'] = used_data
        return data     
    

class ClassesSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.IntegerField(write_only=True)    
    class_id = serializers.PrimaryKeyRelatedField(source='pk',read_only=True)
    schedule = Class_ScheduelSerializer(source = "scheduel",read_only=True,many=True)
    class Meta:
        model = Classes
        fields = ['class_id','name','description','registration_fee',
                'branch','branch_id','image_path','points','schedule'] 


class CreateClassSerializer(serializers.ModelSerializer): 
    schedule = Class_ScheduelSerializer(source='scheduel', many=True)

    class Meta:
        model = Classes
        fields = [
            'name', 'description', 'registration_fee',
            'image_path', 'points', 'schedule'
        ]

    def create(self, validated_data):
        schedule_data = validated_data.pop('scheduel', None)
        branch_id = self.context.get('branch_id')
        class_id = Classes.objects.create(branch_id = branch_id , **validated_data)
        
        for schedule in schedule_data:
            Class_Scheduel.objects.create(class_id=class_id, **schedule)
        return class_id
    

class ClientClassesSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.IntegerField(write_only=True)    
    class_id = serializers.PrimaryKeyRelatedField(source='pk',read_only=True)
    schedule = Class_ScheduelSerializer(source = "scheduel",read_only=True,many=True)
    class Meta:
        model = Classes
        fields = ['class_id','name','description','registration_fee',
                'branch','branch_id','image_path','points','schedule'] 

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        print(representation)
        try:
            now = datetime.datetime.now().date()
            for date in representation['schedule']:
                allowed_date = datetime.datetime.strptime(date['start_date'],'%Y-%m-%d').date() + relativedelta(days=date['allowed_days_to_cancel'])
                if now > allowed_date:
                    representation['schedule'].remove(date)
                elif date['current_number_of_trainees'] >= date['allowed_number_for_class']:
                    representation['schedule'].remove(date)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        if len(representation['schedule']) > 0:
            return representation    
        
        
        
class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classes
        fields = ['id','name','description','registration_fee','branch','image_path','points']
        
        
class SchduleSerializer(serializers.ModelSerializer):
    classes = ClassSerializer(source='class_id')
    trainer = serializers.CharField(source='trainer.employee.user.username')
    class Meta:
        model = Class_Scheduel
        fields = ['pk','start_time','end_time'
                  ,'trainer','days_of_week'
                  ,'start_date','end_date','hall','allowed_number_for_class',
                  'allowed_days_to_cancel','classes']

class ClassRegisterSerializer(serializers.ModelSerializer):
    class_data = serializers.SerializerMethodField()
    class_schedule_id = serializers.PrimaryKeyRelatedField(source='class_id',queryset =Class_Scheduel.objects.filter(is_deleted=False),required=True)
    vouchers = serializers.ListField(
        child = serializers.CharField()
        ,write_only=True
    )
    class Meta: 
        model = Client_Class
        fields = ['client','class_schedule_id','class_data','vouchers','total','offered_total']
        
    
    def get_class_data(self,obj):
        try:
            schdule = Class_Scheduel.objects.get(pk=obj.class_id.pk,is_deleted=False)
            return {
                'class_schedule':SchduleSerializer(schdule).data
            }
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    
    def create(self,data):
        try:
            instance = RegistrationClassService.register(data)
            return instance
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    
    def update(self,instance,data):
        try:
            if data['class_id'].pk == instance.class_id.pk:
                raise serializers.ValidationError('you are already registered in this class')
            UpdateRegistrationService.update(data,instance)
            return
        except Exception as e:
            raise serializers.ValidationError(str(e))