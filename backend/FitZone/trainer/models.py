from django.db import models
from user.models import Client 
from gym.models import Trainer

class Client_Trainer(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="TraineesRegistrations")
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="TrainersRegistrations")
    start_hour = models.TimeField(null=True)
    end_hour = models.TimeField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)    
    registration_type = models.CharField(max_length=30)
    registration_status = models.CharField(max_length=20,default='pending')
    rejection_reason = models.CharField(max_length=100, null=True)
    