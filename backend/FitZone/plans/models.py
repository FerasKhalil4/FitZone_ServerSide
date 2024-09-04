from django.db import models
from user.models import Client
from gym.models import Gym, Trainer
from equipments.models import Equipment
from disease.models import Limitations, Client_Disease
from equipments.models import Equipment_Exercise
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from datetime import datetime
class Training_plan(models.Model):
    notes = models.TextField(blank=True)
    
class Gym_Training_plans(models.Model):
    gym = models.OneToOneField(Gym , on_delete=models.CASCADE,related_name="gymPlans" )
    training_plan = models.OneToOneField(Training_plan, on_delete=models.CASCADE, related_name= "planGym")
    plan_duration_weeks = models.PositiveIntegerField(default=0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['training_plan','gym'],name='training_plan_gym')
        ]

class Gym_plans_Clients(models.Model):
    gym_training_plan = models.ForeignKey(Gym_Training_plans, on_delete=models.CASCADE, related_name="clients")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="gymPlans")
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
        
    def save(self,*args, **kwargs):
        print('in model')
        if self.end_date is None:
            self.end_date = datetime.now().date() + relativedelta(weeks=self.gym_training_plan.plan_duration_weeks)
        super().save(*args, **kwargs)           
            
class Workout(models.Model):
    training_plan = models.ForeignKey(Training_plan, on_delete=models.CASCADE,related_name="workouts")
    name = models.CharField(max_length=50,null=True)
    order = models.PositiveIntegerField(default=0)
    is_rest = models.BooleanField(default=False)
    has_cardio = models.BooleanField(default=False)
    cardio_duration = models.PositiveIntegerField(blank=True,null=True)
    same_as_order = models.PositiveIntegerField(null=True)
    
    def clean(self):
        super().clean()
        rest = True
        if self.is_rest is False and self.same_as_order is not None:
            rest = None 
        print(rest)
        check = sum(attr is not None for attr in [rest, self.same_as_order])
        if check != 1:
            raise ValidationError('please either provide the same_as_order or is_rest')
        if self.is_rest and (self.has_cardio or self.cardio_duration):
            raise ValidationError('rest workout cannot have cardio or duration')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['training_plan', 'name', 'order'], name='unique_workout_name_order')
        ]
    
    
class Workout_Exercises(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="exercises")
    exercise = models.ForeignKey(Equipment_Exercise, on_delete=models.CASCADE, related_name="workouts")
    sets = models.PositiveIntegerField(default=0)
    reps = models.JSONField(default=dict)
    rest_time_seconds = models.IntegerField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['workout', 'exercise', 'order'], name='unique_workout_exercise_order')
        ]
    
    def check_equipment_limitaiotns(self):
        exercise_limitations = Limitations.objects.filter(exercise=self.exercise)
        exercise_diseases = [limitations.disease.pk for limitations in exercise_limitations]
        client_diseases = Client_Disease.objects.filter(client=self.workout.training_plan.TrainersClientsPlans.client.pk,
                                                        disease__in=exercise_diseases).values_list('disease__name', flat=True)

        diseases =f'{','.join([disease for disease in client_diseases])}' 
        if client_diseases.exists():
            raise ValidationError(f'this client has {diseases} he cant train this exercise {self.exercise.exercise.name} on {self.exercise.equipment.name}')

    def clean(self):
        
        super().clean()
        clients_plan = Client_Trianing_Plan.objects.filter(training_plan =self.workout.training_plan)
        if clients_plan.exists():
            self.check_equipment_limitaiotns()
            
         
        
        
    def save(self, *args, **kwargs):
        self.clean()
        
        super().save(*args, **kwargs)
    
class Client_Trianing_Plan(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="PrivateTrainingPlans")
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="clientsPlans")
    training_plan = models.OneToOneField(Training_plan, on_delete=models.CASCADE, related_name="TrainersClientsPlans")  
    start_date = models.DateField(blank=True)
    end_date = models.DateField(null=True)  
    is_active = models.BooleanField(default=True)
    plan_duration_weeks = models.IntegerField(default=0)
    
    

    def save(self, *args, **kwargs):
        self.clean()
        if self.start_date and self.plan_duration_weeks:
            self.end_date = self.start_date + relativedelta(weeks=self.plan_duration_weeks)
        super().save(*args, **kwargs)