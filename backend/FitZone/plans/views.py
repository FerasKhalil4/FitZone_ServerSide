from rest_framework import generics, status 
from rest_framework.response import Response
from .serializers import *
from .DataExamples import * 
from trainer.models import Client_Trainer
from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import  extend_schema


class PlanMixin():
    def check_incompatibility(self,data):
        if (data['has_cardio'] == True and data['cardio_duration'] is None ) or \
                                (data['has_cardio'] == False and data['cardio_duration'] is not None )\
                                    or(data['has_cardio'] == True and data['cardio_duration'] is not None and data['name']=='Rest') :
            raise ValueError('there is uncomapible data for cardio entered')
        return True
    def check_order_overlap(self, check_overlap_order ,order):
    
        check_overlap_order.order = order
        check_overlap_order.save()
        return True
    
    def check_on_workout(self, workouts):
        if len(workouts) != 7 :
            raise ValueError('there should be 7 items in workouts')
        return True

    def Create_Training_plan(self,data):
        try:
            plan_serializer = TrainingPlanSerializer(data=data)
            plan_serializer.is_valid(raise_exception=True)
            plan = plan_serializer.save()
            return plan
        except Exception as e:
            raise ValueError(str(e))
    
    
    def Create_Workouts(self,workouts,plan):
        
        for i in range(len(workouts)):
            if 'name' not in workouts[i]:
                workouts[i]['name'] = 'Rest'
                
        for workout in workouts:
            exercises = workout.pop('exercises',[])
            workout['training_plan'] = plan.pk
            self.check_incompatibility(workout)
            
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
                    raise ValueError('please add the exercises for this plan')
        return True
    def check_client_existing_plan(self,client):
        today = datetime.datetime.now().date()
        query = Q(
            start_date__lte = today, 
            end_date__gte = today ,
            client = client,
            is_active = True,
        )
        check = Client_Trianing_Plan.objects.filter(query)
        gym_plans = Gym_plans_Clients.objects.filter(query)
        if check.exists() or gym_plans.exists():
            raise LookupError('Client already has a training plan') 
        
        return True
    
    def check_client_availabilty(self, trainer, client):
        today = datetime.datetime.now().date()
        query= Q(
            trainer=trainer ,
            client=client,
            registration_status='accepted',
            end_date__gte = today
        )
        check_availability = Client_Trainer.objects.filter(query)  
        if check_availability.exists():
            return True     
        else:
            raise LookupError('the client does not available')    
        
    def update_training_plan(self,training_plan_instance,data):
        try:
            serializer = TrainingPlanSerializer(training_plan_instance,data =data, partial = True)
            serializer.is_valid(raise_exception=True)
            serializer.save() 
            return True
        except Exception as e: 
            raise ValueError (str(e))
    
    def get_training_plan(self,plan_id):
        try:
            plan_instance = Training_plan.objects.get(id = plan_id)
            serializer = TrainingPlanSerializer(plan_instance)
            return serializer.data
        except Exception as e:
            return ValueError(str(e))
        
class Gym_TrainingPlanCreateAV(PlanMixin,generics.CreateAPIView):
    serializer_class = Gym_Training_plansSerializer
    
    def get_queryset(self):
        return  Gym_Training_plans.objects.filter(gym = self.kwargs['gym_id'])

        
    @extend_schema(
    summary="create  the training plan related to the gym",
    examples=create_training_plan
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
                
                self.check_on_workout(workouts)
                plan = self.Create_Training_plan(data)

                gym_plan_data = {
                    'gym':gym_id,
                    'training_plan':plan.pk,
                    'plan_duration_weeks':data.get('plan_duration_weeks')
                }
                
                gym_training_plan_serializer = Gym_Training_plansSerializer(data=gym_plan_data)
                gym_training_plan_serializer.is_valid(raise_exception=True)
                gym_training_plan_serializer.save()
                
                self.Create_Workouts(workouts, plan)
                
                return Response({'message':'training plan created successfully'},status=status.HTTP_201_CREATED)
                            
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
gymPlanCreate = Gym_TrainingPlanCreateAV.as_view()
        
class Gym_planDetailsAV(PlanMixin,generics.RetrieveUpdateAPIView):
    queryset = Gym_Training_plans.objects.all()
    serializer_class = Gym_Training_plansSerializer
    @extend_schema(
        summary="get the training plan related to the gym",
   )
    def get(self, request, *args, **kwargs):
        try:
            return Response (self.get_training_plan(kwargs.get('plan_id')), status=status.HTTP_200_OK)
        except Exception as e :
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
    summary="update the training plan related to the gym ",
    examples=update_the_training_plan

    )
            
    def put(self,request, *args, **kwargs):
        try:
            with transaction.atomic():        
                plan_id  = kwargs.pop('plan_id')
                data=request.data
                training_plan_instance = Training_plan.objects.get(id = plan_id)
                
                self.update_training_plan(training_plan_instance,data)
                
                gym_training_plan_instance = Gym_Training_plans.objects.get(training_plan = training_plan_instance.pk)
                gym_serializer = Gym_Training_plansSerializer(gym_training_plan_instance,data =data,partial=True)
                gym_serializer.is_valid(raise_exception=True)
                gym_serializer.save()
                
                return Response({'success':'plan updated successfully'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

gymPlanDetails = Gym_planDetailsAV.as_view()


class WorkoutDetailsAV(PlanMixin,generics.RetrieveUpdateAPIView):
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
                    self.check_order_overlap(check_overlap_order,workout_instance.order)
                self.check_incompatibility(data)
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

class ClientTrainingPlanCreateAV(PlanMixin,generics.CreateAPIView):
    serializer_class = ClientTrainingSerializer
    queryset = Client_Trianing_Plan.objects.all()
    
    @extend_schema(
        summary='create training plan for client',
        examples= create_training_plan
    )
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data 
                client = Client.objects.get(pk = kwargs.get('client_id'),user__is_deleted=False)
                user = request.user
                trainer = Trainer.objects.get(employee__user=user)   
                workouts = data.pop('workouts', [])
                
                self.check_client_availabilty(trainer,client )
                self.check_client_existing_plan(client)
                self.check_on_workout(workouts)
                plan = self.Create_Training_plan(data)
                
                client_plan_data = {
                    'client':client.pk,
                    'trainer':trainer.pk,                    
                    'training_plan':plan.pk,
                    'plan_duration_weeks':data.get('plan_duration_weeks'),
                    'start_date':datetime.datetime.now().date(),
                }
                
                client_plan_data = ClientTrainingSerializer(data=client_plan_data)
                client_plan_data.is_valid(raise_exception=True)
                client_plan_data.save()
                
                self.Create_Workouts(workouts, plan)
                
                return Response({'success': 'Trianing plan created successfully'},status=status.HTTP_201_CREATED)
                
        except Client.DoesNotExist:
            return Response({'error':'client does not exist'},status=status.HTTP_400_BAD_REQUEST)    
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)     
         
clientTrainingPlan= ClientTrainingPlanCreateAV.as_view()


class ClientTrainingPlanDetailsAV(PlanMixin,generics.RetrieveUpdateAPIView):
    queryset = Client_Trianing_Plan.objects.all()
    serializer_class = ClientTrainingSerializer
    @extend_schema(
        summary="get the training plan related to the client",
   )
    def get(self, request, *args, **kwargs):
        try:
            data=self.get_training_plan(kwargs.get('plan_id'))
            return Response (data, status=status.HTTP_200_OK)
        except Exception as e :
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    
    
    @extend_schema(
    summary="update the training plan related to the client",
    examples=update_the_training_plan

    )
            
    def put(self,request, *args, **kwargs):
        try:
            with transaction.atomic():        
                plan_id  = kwargs.pop('plan_id')
                training_plan_instance = Training_plan.objects.get(id = plan_id)
                data = request.data
                self.update_training_plan(training_plan_instance,data)
                
                ClientTraining_instance = Client_Trianing_Plan.objects.get(training_plan = training_plan_instance.pk)
                if ClientTraining_instance.plan_duration_weeks != data['plan_duration_weeks']:
                    data['end_date'] = ClientTraining_instance.start_date + relativedelta(weeks=data['plan_duration_weeks'])
                    
                client_serializer = ClientTrainingSerializer(ClientTraining_instance,data =data,partial=True)
                client_serializer.is_valid(raise_exception=True)
                client_serializer.save()
                
                return Response({'success':'plan updated successfully'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)

ClientTrainingPlanDetails = ClientTrainingPlanDetailsAV.as_view()


class PlanUpdateStatusAV(generics.UpdateAPIView):
    serializer_class = ClientTrainingSerializer
    queryset = Client_Trianing_Plan.objects.all()
    
    @extend_schema(
        summary='update the status of the training plan',
        examples=update_the_status
    )
    def put(self,request, *args, **kwargs):
        try:
            plan_status = request.data.get('is_active')
            pk = kwargs.get('client_plan_id')
            instance = Client_Trianing_Plan.objects.get(pk=pk)
            instance.is_active = plan_status
            instance.save()
            return Response({'success':'plan status updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
planstatus = PlanUpdateStatusAV.as_view()
        
    
