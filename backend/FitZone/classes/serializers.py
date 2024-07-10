from rest_framework import serializers 
from .models import Classes
from gym.seriailizers import EmployeeSerializer, BranchSerializer
from gym.models import Employee , Shifts ,Gym , Branch
from user.serializers import ClientSerializer
from django.db.models import Q
from datetime import date
import json 

from django.db.models import Count
from django.db import connection
class ClassesSerializer(serializers.ModelSerializer):
    trainer = EmployeeSerializer(read_only=True)
    clients = ClientSerializer(read_only=True, many = True)
    branch = BranchSerializer(read_only=True)
    trainer_id = serializers.IntegerField(write_only=True)
    branch_id = serializers.IntegerField(write_only=True)    
    start_time = serializers.TimeField(input_formats=["%H:%M:%S"])
    end_time = serializers.TimeField(input_formats=["%H:%M:%S"])
    start_date = serializers.DateField(input_formats=["%Y-%m-%d"])
    end_date = serializers.DateField(input_formats=["%Y-%m-%d"])
    
    class Meta:
        model = Classes
        fields = ['name','description','start_time','end_time','trainer','registration_fee','clients' , 'hall' , 'days_of_week'
                  ,'start_date','end_date','branch','trainer_id','branch_id']
        

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
            if len(days) != len(set(days)):
                raise serializers.ValidationError({"error": "please check on the days entered"})
            for day in days:
                if day not in days_of_week.values():
                    raise serializers.ValidationError({"error": "please check on the days entered"})
        
        def get_gym_details(user):
            try:
                employee = Employee.objects.get(user=user)
                branch = Shifts.objects.filter(employee=employee).first().branch_id
                gym_id = Branch.objects.get(id=branch).gym_id
                return Gym.objects.get(id=gym_id)
            except Exception as e:
                raise serializers.ValidationError({'error': str(e)})
        
        def check_time_validity(gym, start_time, end_time):
            if start_time >= end_time:
                raise serializers.ValidationError({'error': 'Invalid start time'})
            if not (gym.start_hour <= start_time < gym.close_hour) or not (gym.start_hour < end_time <= gym.close_hour):
                raise serializers.ValidationError({'error': 'please check on the schedule of the gym and the entered class data'})
        
        def check_date_validity(start_date, end_date):
            if start_date <= date.today():
                raise serializers.ValidationError('Start date should be greater than or equal to today.')
            if end_date <= start_date:
                raise serializers.ValidationError('End date should be greater than start date.')
            
        def days_of_week_overlap(value):
            query = Q()
            for day , day_name in value.items():
                query |= Q(days_of_week__contains= {day:day_name})
            return query

        def check_overlap(data, used_data):
            overlap_con = (
                Q(
                hall = data['hall'],
                start_date__lte = data['start_date'],
                end_date__gt = data['start_date'],
                trainer = data['trainer_id'],
            )&(Q(start_time__lte = data['start_time'], end_time__gt = data['start_time'])
                | Q(start_time__lt = data['end_time'], end_time__gte = data['end_time'])
                | Q(start_time__gte = data['start_time'], end_time__lte = data['end_time'])
            )&
                days_of_week_overlap(used_data) 
            )|(
                Q(
                start_date__lt = data['end_date'],
                end_date__gte = data['end_date'],
                 hall=data['hall'],
                trainer = data['trainer_id'],
            )&(
                Q(start_time__lte = data['start_time'], end_time__gt = data['start_time'])
                | Q(start_time__lt = data['end_time'], end_time__gte = data['end_time'])
                | Q(start_time__gte = data['start_time'], end_time__lte = data['end_time'])
            )&
                days_of_week_overlap(used_data) 
           
            )|(
                Q(
                hall = data['hall'],
                start_date__gte = data['start_date'],
                end_date__lte = data['end_date'],
                trainer = data['trainer_id'],
            )&( Q(start_time__lte = data['start_time'], end_time__gt = data['start_time'])
                 | Q(start_time__lt = data['end_time'], end_time__gte = data['end_time'])
                 | Q(start_time__gte = data['start_time'], end_time__lte = data['end_time'])
                 )&
            days_of_week_overlap(used_data)
            )
            instance_ = self.context.get('instance') or None
            if instance_ is not None:
                instance = instance_.id
                overlap_con &= ~Q(id=instance) 
            overlapped_classed = Classes.objects.filter(overlap_con)
            if overlapped_classed.exists():
                raise serializers.ValidationError('This class overlaps with another one in the same hall and date range.')

        days = list(data.get('days_of_week').values())
        validate_days(days)
        
        if data['registration_fee'] < 0:
            raise serializers.ValidationError({"error": "please check on the registration_fee entered, it must be a positive value"})
        
        used_data = get_used_data(data['days_of_week'])
        
        request = self.context.get('request')
        user = request.user
        gym = get_gym_details(user)        
        check_time_validity(gym, data['start_time'], data['end_time'])
        check_date_validity(data['start_date'], data['end_date'])
        check_overlap(data, used_data)
        
        data['days_of_week'] = used_data
        return data          