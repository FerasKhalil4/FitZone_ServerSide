from django.db import models
from user.models import Client
from gym.models import Gym, Trainer
from equipments.models import Equipment_Exercise
from django.db.models import UniqueConstraint

class Training_plan(models.Model):
    notes = models.TextField(blank=True)
    
class Gym_Training_plans(models.Model):
    gym = models.ForeignKey(Gym , on_delete=models.CASCADE,related_name="gymPlans" )
    training_plan = models.OneToOneField(Training_plan, on_delete=models.CASCADE, related_name= "planGym")
    plan_duration_weeks = models.PositiveIntegerField(default=0)

class Gym_plans_Clients(models.Model):
    gym_training_plan = models.ForeignKey(Training_plan, on_delete=models.CASCADE, related_name="clients")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="gymPlans")
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True)
    
class Workout(models.Model):
    training_plan = models.ForeignKey(Training_plan, on_delete=models.CASCADE,related_name="workouts")
    name = models.CharField(max_length=50,null=True)
    order = models.PositiveIntegerField(default=0)
    is_rest = models.BooleanField(default=False)
    has_cardio = models.BooleanField(default=True)
    cardio_duration = models.PositiveIntegerField(blank=True,null=True)
    
class Workout_Exercises(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="exercises")
    exercise = models.ForeignKey(Equipment_Exercise, on_delete=models.CASCADE, related_name="workouts")
    sets = models.PositiveIntegerField(default=0)
    reps = models.JSONField(default=dict)
    rest_time_seconds = models.IntegerField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    
class Client_TrianingPlan(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="PrivateTrainingPlans")
    Trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="clientsPlans")
    training_plan = models.OneToOneField(Training_plan, on_delete=models.CASCADE, related_name="TrainersClientsPlans")    