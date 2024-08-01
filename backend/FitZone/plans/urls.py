from django.urls import path
from .views import * 

urlpatterns = [
    path('gym/<int:gym_id>/', gymPlanCreate, name='gymPlanCreate'),
    path('gym-details/<int:plan_id>/',gymPlanDetails,name='gymPlanDetails'),
    path('workout/<int:workout_id>/', workoutDetails, name='workoutDetails'),
    path('workout/exercise-create/<int:workout_id>/',workoutExercisesCreate, name='workoutExercisesCreate'),
    path('workout/exercise-update/<int:workout_exercises_id>/',ExerciseWorkoutDetails,name='destoryExerciseWorkout'),
    path('training/client/<int:client_id>/',clientTrainingPlan, name='clientTrainingPlan'),
    path('training-details/client/<int:plan_id>/',ClientTrainingPlanDetails,name='ClientTrainingPlanDetails'),
    path('status/update/<int:client_plan_id>/',planstatus,name='planstatus')
]
