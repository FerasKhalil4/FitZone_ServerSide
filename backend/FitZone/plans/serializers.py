from rest_framework import serializers
from .models import *
from equipments.serializers import Equipment_ExerciseSerializer


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
        fields = ['workout_id','training_plan','name','exercises','order','is_rest','has_cardio','cardio_duration']
                
class Gym_plans_ClientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gym_plans_Clients
        fields = ['client','gym_training_plan','start_date','end_date']
        
class Gym_Training_plansSerializer(serializers.ModelSerializer):
    clients = Gym_plans_ClientsSerializer(source = "clients.client",read_only=True,many=True)
    gym_training_id = serializers.PrimaryKeyRelatedField(source="id",read_only=True)
    
    class Meta:
        model = Gym_Training_plans
        fields = ['gym_training_id','training_plan','gym','training_plan','clients','plan_duration_weeks']
        
                
class TrainingPlanSerializer(serializers.ModelSerializer):
    workouts = WorkoutSerializer(read_only=True , many=True)
    plan_id = serializers.PrimaryKeyRelatedField(source="id",read_only=True)
    planGym = Gym_Training_plansSerializer(read_only=True)
    
    class Meta:
        model = Training_plan
        fields = ['plan_id','notes','workouts','planGym']


