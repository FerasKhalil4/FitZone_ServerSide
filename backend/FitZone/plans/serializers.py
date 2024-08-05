from rest_framework import serializers
from .models import *
from equipments.serializers import Equipment_ExerciseSerializer
from gym.seriailizers import GymSerializer
import datetime

class Workout_ExercisesSerializer(serializers.ModelSerializer):
    exercises_details = Equipment_ExerciseSerializer(source="exercise", read_only=True)
    Workout_Exercises_id = serializers.PrimaryKeyRelatedField(source="id",read_only=True)
    
    class Meta:
        model = Workout_Exercises
        fields = ['Workout_Exercises_id','exercise','workout','sets','reps','order','exercises_details','rest_time_seconds']
        
    def validate(self,data):
        if data['sets'] != len(data['reps']):
            raise serializers.ValidationError('mismatch between sets and the reps data')
        for rep in data['reps'].values():
            if rep < 0 :
                raise serializers.ValidationError('please check on the reps data they should be positive values')
        return data        

class WorkoutSerializer(serializers.ModelSerializer):
    exercises = Workout_ExercisesSerializer(read_only=True,many=True)
    workout_id = serializers.PrimaryKeyRelatedField(source="id",read_only=True)
    class Meta:
        model = Workout
        fields = ['workout_id','training_plan','name','exercises','order','is_rest','has_cardio','cardio_duration','same_as_order']
                
class Gym_plans_ClientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gym_plans_Clients
        fields = ['client','gym_training_plan','start_date','end_date','is_active']
        
        
class TrainingPlanSerializer(serializers.ModelSerializer):
    workouts = WorkoutSerializer(read_only=True , many=True)
    plan_id = serializers.PrimaryKeyRelatedField(source="id",read_only=True)
    
    class Meta:
        model = Training_plan
        fields = ['plan_id','notes','workouts']
        
class ClientTrainingSerializer(serializers.ModelSerializer):
    client_train_plan_id = serializers.PrimaryKeyRelatedField(source="id",read_only=True)
    training_plan_data = TrainingPlanSerializer(source="training_plan", read_only=True)
    class Meta:
        model = Client_Trianing_Plan
        fields = ['client_train_plan_id','training_plan'
                  ,'start_date','end_date','trainer','client','is_active','plan_duration_weeks','training_plan_data']
    
    def validate_start_date(self,data):
        today = datetime.datetime.now().date()
        if data < today:
            raise serializers.ValidationError('Start date must be greater than today')
        return data
        

class Gym_Training_plansSerializer(serializers.ModelSerializer):
    clients = Gym_plans_ClientsSerializer(source = "clients.client",read_only=True,many=True)
    gym_training_id = serializers.PrimaryKeyRelatedField(source="id",read_only=True)
    training_plan_data = TrainingPlanSerializer(source="training_plan",read_only=True)
    class Meta:
        model = Gym_Training_plans
        fields = ['gym_training_id','training_plan','gym','clients','plan_duration_weeks','training_plan_data']
        
