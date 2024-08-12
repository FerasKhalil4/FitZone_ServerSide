from django.db import models
from gym.models import Trainer
from user.models import Client
from django.db.models import UniqueConstraint
from dateutil.relativedelta import relativedelta
import datetime

class NutritionPlan(models.Model):
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='nutrition_plans')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='nutrition_plans')
    name = models.CharField(max_length=20)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    weeks_number = models.PositiveIntegerField(default=0)
    notes = models.TextField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_same = models.BooleanField(default=False)
    
    def save(self,*args, **kwargs):
        if self.start_date is None and self.weeks_number:
            self.start_date = datetime.datetime.now().date()
            self.end_date = self.start_date + relativedelta(weeks=self.weeks_number)
        super().save(*args, **kwargs)
    
class MealsSchedule(models.Model):
    nutrition_plan = models.ForeignKey(NutritionPlan, on_delete=models.CASCADE, related_name='meals_schedules')
    day = models.PositiveIntegerField(default=0)
    same_as_day = models.PositiveIntegerField(null=True)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['nutrition_plan', 'day'], name='unique_day_per_week'),
        ]
    
class MealsType(models.Model):
    MEALS_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Brunch', 'Brunch'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
        ('Snack', 'Snack'),
        ('Pre-Workout', 'Pre-Workout'),
        ('Post-Workout', 'Post-Workout'),
    ]
    meals_schedule = models.ForeignKey(MealsSchedule, on_delete=models.CASCADE, related_name='meals_types')
    type = models.CharField(max_length=50, choices=MEALS_CHOICES)
    is_deleted = models.BooleanField(default=False)
    
    def delete(self,*args, **kwargs):
        if self.is_deleted is False:
            self.is_deleted = True
            self.save()
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['meals_schedule', 'type'], name='unique_meal_per_day'),
        ]

class Meals(models.Model):
    meals_type = models.ForeignKey(MealsType, on_delete=models.CASCADE, related_name='meals')
    name = models.CharField(max_length=30)
    portion_size = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    portion_unit = models.CharField(max_length=20)
    alternateives = models.JSONField(default=dict)
    is_deleted = models.BooleanField(default=False)
    
    def delete(self,*args, **kwargs):
        if self.is_deleted is False:
            self.is_deleted = True
            self.save()
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['meals_type', 'name'], name='unique_meal_per_type'),
        ]
    
    


    
