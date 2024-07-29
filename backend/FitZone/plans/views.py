from rest_framework import generics, status 
from rest_framework.response import Response
from .serializers import *
from .DataExamples import * 
from django.db import transaction
from drf_spectacular.utils import  extend_schema

def check_order_overlap(check_overlap_order ,order):
    
    check_overlap_order.order = order
    check_overlap_order.save()
    return True
                

class Gym_TrainingPlanCreateAV(generics.CreateAPIView):
    serializer_class = Gym_Training_plansSerializer
    
    def get_queryset(self):
        return  Gym_Training_plans.objects.filter(gym = self.kwargs['gym_id'])

        
    @extend_schema(
    summary="create  the training plan related to the gym",
    examples=create_gym_training_plan
)
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                
                gym_id = self.kwargs['gym_id']
                check  = Gym_Training_plans.objects.filter(gym=gym_id)
                if check.exists():
                    return Response({'error':'this gym already has base training plan'},status=status.HTTP_400_BAD_REQUEST)
                data = request.data
                workouts = data.pop('workouts', [])
                if len(workouts) != 7 :
                    return Response({'error':'there should be 7 items in workouts'},status=status.HTTP_400_BAD_REQUEST)
                for i in range(len(workouts)):
                    if 'name' not in workouts[i]:
                        workouts[i]['name'] = 'Rest'

                plan_serializer = TrainingPlanSerializer(data=data)
                plan_serializer.is_valid(raise_exception=True)
                plan = plan_serializer.save()
                
                gym_plan_data = {
                    'gym':gym_id,
                    'training_plan':plan.pk,
                    'plan_duration_weeks':data.get('plan_duration_weeks')
                }
                
                gym_training_plan_serializer = Gym_Training_plansSerializer(data=gym_plan_data)
                gym_training_plan_serializer.is_valid(raise_exception=True)
                gym_training_plan_serializer.save()
                
                for workout in workouts:
                                        
                    exercises = workout.pop('exercises',[])
                    workout['training_plan'] = plan.pk
                    if (workout['has_cardio'] == True and workout['cardio_duration'] is None) or \
                                            (workout['has_cardio'] == False and workout['cardio_duration'] is not None) :
                        return Response({'error':'there is incomapible data for cardio entered'}, status=status.HTTP_400_BAD_REQUEST)
                    workout_serializer = WorkoutSerializer(data=workout)
                    workout_serializer.is_valid(raise_exception=True)
                    workout_instance = workout_serializer.save()
                    if workout_instance.name != 'Rest':
                        if exercises is not [] :
                            for exercise in exercises:
                                exercise['workout'] = workout_instance.pk
                                
                                exercise_serializer = Workout_ExercisesSerializer(data = exercise)
                                exercise_serializer.is_valid(raise_exception=True)
                                exercise_serializer.save()
                        else:
                            return Response({'error':'please add the exercises for this plan'},status=status.HTTP_400_BAD_REQUEST)
                    
                return Response({'message':'traingin plan created successfully'},status=status.HTTP_201_CREATED)
                            
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
gymPlanCreate = Gym_TrainingPlanCreateAV.as_view()
        
class Gym_planDetailsAV(generics.RetrieveUpdateAPIView):
    queryset = Gym_Training_plans.objects.all()
    serializer_class = Gym_Training_plansSerializer
    @extend_schema(
        summary="get the training plan related to the gym",
   )
    def get(self, request, *args, **kwargs):
        try:
            plan_id  = kwargs.pop('plan_id', None)
            plan_instance = Training_plan.objects.get(id = plan_id)
            serializer = TrainingPlanSerializer(plan_instance)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
    summary="update the training plan related to the gym with workouts",
    examples=update_the_training_plan

    )
            
    def put(self,request, *args, **kwargs):
        try:
            with transaction.atomic():        
                plan_id  = kwargs.pop('plan_id')
                training_plan_instance = Training_plan.objects.get(id = plan_id)
                data = request.data
                serializer = TrainingPlanSerializer(training_plan_instance,data =data, partial = True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                gym_training_plan_instance = Gym_Training_plans.objects.get(training_plan = training_plan_instance.pk)
                gym_serializer = Gym_Training_plansSerializer(gym_training_plan_instance,data =data,partial=True)
                gym_serializer.is_valid(raise_exception=True)
                gym_serializer.save()
                
                return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

gymPlanDetails = Gym_planDetailsAV.as_view()


class WorkoutDetailsAV(generics.RetrieveUpdateAPIView):
    serializer_class = WorkoutSerializer
    queryset =  Workout.objects.all()
    
    @extend_schema(
        summary="get specific workout",
   )
    def get(self, request, *args, **kwargs):
        try:
            workout_id = kwargs.pop('workout_id', None)
            workout_instance = Workout.objects.get(id = workout_id)
            serializer = WorkoutSerializer(workout_instance)
            return Response(serializer.data,status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        summary="update specific workout",
        examples=update_workout
   )
    def put(self, request, *args, **kwargs):
        try:
            with transaction.atomic():       
                data = request.data
                         
                workout_id = kwargs.pop('workout_id', None)
                workout_instance = Workout.objects.get(id = workout_id)
                check_overlap_order = Workout.objects.filter(id = workout_instance.pk ,order = data['order']).first()
                if check_overlap_order :
                    check_order_overlap(check_overlap_order,workout_instance.order)
                        
                if (data['has_cardio'] == True and data['cardio_duration'] is None ) or \
                                            (data['has_cardio'] == False and data['cardio_duration'] is not None )\
                                            or(data['has_cardio'] == True and data['cardio_duration'] is not None and data['name']=='Rest') :
                        return Response({'error':'there is incomapible data for cardio entered'}, status=status.HTTP_400_BAD_REQUEST)
                if data['name'] != 'Rest' and data['is_rest']==True:
                    return Response({'error':'there is incomapible data for the workout the rest day shouldnt be true'}, status=status.HTTP_400_BAD_REQUEST)

                serializer = WorkoutSerializer(workout_instance,data = data, partial = True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                if data['name'] == 'Rest':
                    workout_exercises_instance = Workout_Exercises.objects.filter(workout_id=workout_id)
                    workout_exercises_instance.delete()
                return Response(serializer.data,status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

workoutDetails = WorkoutDetailsAV.as_view()


class WorkoutExercisesCreateAV(generics.CreateAPIView):
    serializer_class = Workout_ExercisesSerializer
    
    @extend_schema(
    summary="add exercise to workout",
    examples=Exercise_to_workout_plan

    )
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                workout_id = kwargs.pop('workout_id', None)
                instance = Workout_Exercises.objects.filter(workout_id=workout_id,order=data['order']).first()
                if instance :
                    updated_exercises = Workout_Exercises.objects.filter(workout = workout_id , order__gte = data['order'])
                    for exercise_ in updated_exercises: 
                        exercise_.order +=1
                        exercise_.save()
                data['workout'] = workout_id
                serializer = Workout_ExercisesSerializer(data = data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'message':'exercise is added to the plan successfully','data':serializer.data},status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

workoutExercisesCreate = WorkoutExercisesCreateAV.as_view()


class ExerciseWorkoutDetailsAV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = Workout_ExercisesSerializer
    queryset = Workout_Exercises.objects.all()
    def get_object(self):
        try:
            return Workout_Exercises.objects.get(pk=self.kwargs['workout_exercises_id'])
        except Exception as e:
            raise serializers.ValidationError('instance does not exist')
    @extend_schema(
        summary="get specific exercise",
   )
    def get(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data,status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="update specific exercise",
        examples=Exercise_to_workout_plan
   )
    def put (self,request, *args, **kwargs):
        try:
            with transaction.atomic():
                workout_exercise_instance = self.get_object()
                data = request.data
                check_order_overlap =  Workout_Exercises.objects.filter(workout = workout_exercise_instance.pk , order = data['order'])
                if check_order_overlap.exists():
                    updated_exercises = Workout_Exercises.objects.filter(workout = workout_exercise_instance.pk , order = data['order'])
                    for exercise_ in updated_exercises: 
                        exercise_.order +=1
                        exercise_.save()

                serializer = Workout_ExercisesSerializer(workout_exercise_instance,data = data, partial = True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
    summary="delete specific excercise",
   )
    
    def delete(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance_id = kwargs.get('Workout_Exercises_id')
                workout_exercise_instance = Workout_Exercises.objects.get(pk=instance_id)
                workout_exercise_instance.delete()
                return Response({'message':'exercise deleted successfully'},status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

ExerciseWorkoutDetails = ExerciseWorkoutDetailsAV.as_view()    
    
        