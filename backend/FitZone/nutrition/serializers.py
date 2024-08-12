from rest_framework import serializers 
from .models import * 
import datetime
from user.serializers import ClientSerializer
from gym.seriailizers import TrainerSerialzier
from trainer.models import Client_Trainer

today = datetime.datetime.now().date()

class MealsSerializer(serializers.ModelSerializer):
    meals_id = serializers.PrimaryKeyRelatedField(source = 'id',read_only=True)
    class Meta:
        model = Meals
        fields = ['name','portion_size','portion_unit','meals_id','alternateives']
        
class MealsTypeSerializer(serializers.ModelSerializer):
    meals_type_id = serializers.PrimaryKeyRelatedField(source = 'id',read_only=True)
    meals = MealsSerializer(many=True,required=False,write_only=True)
    meals_data = serializers.SerializerMethodField()
    class Meta:
        model = MealsType
        fields = ['type','meals_type_id','meals','meals_data']
    def get_meals_data(self,obj):
        return MealsSerializer(Meals.objects.filter(is_deleted=False,meals_type=obj),many=True).data
    
    def create(self, validated_data):
        meals = validated_data.pop('meals',None)
        validated_data['meals_schedule'] = MealsSchedule.objects.get(pk = validated_data['meals_schedule'])
        meals_type = MealsType.objects.create(**validated_data)
        
        for meal_data in meals:
            meal_data['meals_type'] = meals_type
            Meals.objects.create(**meal_data)
        return meals_type
        
        
class MealsScheduleSerializer(serializers.ModelSerializer):
    meals_schedule_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    meals_types = MealsTypeSerializer(many=True,write_only=True,required=False)
    same_meals = serializers.SerializerMethodField()
    meals_type_data = serializers.SerializerMethodField()
    class Meta:
        model = MealsSchedule
        fields = ['day', 'meals_schedule_id', 'meals_types','same_as_day','same_meals','meals_type_data']
    
    def get_meals_type_data(self,obj):
        return MealsTypeSerializer(MealsType.objects.filter(is_deleted=False,meals_schedule=obj),many=True).data
    
    def get_same_meals(self,obj):
        if obj.same_as_day is not None:
            return MealsScheduleSerializer(MealsSchedule.objects.filter(day=obj.same_as_day), many=True).data
                
class NutritionPlanSerializer(serializers.ModelSerializer):
    nutrition_plan_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    meals_schedule = MealsScheduleSerializer(source="meals_schedules",many=True,required=False)
    client = ClientSerializer(read_only=True)
    trainer = TrainerSerialzier(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    class Meta: 
        model = NutritionPlan
        fields = [
            'nutrition_plan_id', 'trainer', 'client', 'name',
            'maintain_fats', 'maintain_protein', 'maintain_calories',
            'start_date', 'end_date', 'weeks_number', 'notes', 'is_active', 'meals_schedule','is_same'
        ]
        
    def validate_value(self, value):
        if value <= 0:
            raise serializers.ValidationError(f'{value}must be greater than 0')
        return value
    def check_client_plan(self,client,trainer,today):
        check = NutritionPlan.objects.filter(client=client,start_date__lte = today, end_date__gte = today,is_active=True)
        if check.exists():
            raise serializers.ValidationError('Client plan  is already has active plan')
        check_registration = Client_Trainer.objects.filter(trainer=trainer,client=client,
                                                           start_date__lte=today,end_date__gte=today,
                                                           registration_status='accepted')
        if len(check_registration)!= 1:
            raise serializers.ValidationError('Client is not registered with this trianer')
        return client
    def validate_schedule(self,schedule):
        if len(schedule) != 7 :
            raise serializers.ValidationError('schedule must contain 7 days')
        return schedule
    def validate(self,data):
        self.validate_value(data['maintain_calories'])
        self.validate_value(data['maintain_fats'])
        self.validate_value(data['maintain_protein'])
        # self.validate_schedule(data['meals_schedules'])
        if  data['is_same'] == True and len(data['meals_schedules']) != 1:
            raise serializers.ValidationError('Multiple schedules where added but is_same flag is set to True also ')
        return data
    
        
    def create(self, validated_data):
        client = self.context.get('client')
        trainer = self.context.get('trainer')
        
        self.check_client_plan(client,trainer,today)
        
        meals_schedule_data = validated_data.pop('meals_schedules')
        nutrition_plan = NutritionPlan.objects.create(client=client,trainer=trainer,**validated_data)

        for schedule_data in meals_schedule_data:
            schedule_data['nutrition_plan'] = nutrition_plan  

            if 'meals_types' in schedule_data:
                meals_types_data = schedule_data.pop('meals_types')
            meals_schedule = MealsSchedule.objects.create(**schedule_data)
            
            if meals_schedule.same_as_day is not None:           
                ...
                
            else:
                for meals_type_data in meals_types_data:
                    meals_data = meals_type_data.pop('meals')
                    meals_type_data['meals_schedule'] = meals_schedule
                    meals_type = MealsType.objects.create(**meals_type_data)

                    for meal_data in meals_data:
                        meal_data['meals_type'] = meals_type
                        Meals.objects.create(**meal_data)
            if nutrition_plan.is_same :
                break
        return nutrition_plan
    

class PlanStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionPlan
        fields = ['is_active']
        
