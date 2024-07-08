from django.db import models
from gym.models import Employee, Branch
from user.models import Client
class Classes(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    start_date = models.DateField(blank= True)
    end_date = models.DateField(blank= True)
    registration_fee = models.FloatField(default=0.00)
    trainer=models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='class_trainer')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branch_class')
    start_time = models.TimeField(blank= True)
    end_time = models.TimeField(blank= True)
    days_of_week = models.JSONField(default=dict)
    clients = models.ManyToManyField(Client, related_name='clients')
    hall = models.IntegerField(blank=True)    
    is_deleted = models.BooleanField(default=False)

    
