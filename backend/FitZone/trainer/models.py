from django.db import models
from user.models import Client 
from gym.models import Trainer
import datetime
from django.core.exceptions import ValidationError
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
    
    def clean(self) -> None:
        super().clean()
        today = datetime.datetime.now().date()
        check = Client_Trainer.objects.filter(client=self.client, start_date__lte= today,end_date__gte= today,registration_status='accepted' )
        if check.exists():
            raise ValidationError('this client is already registered with trainer')
        
    def save(self, *args, **kwargs):
        if self.start_date and self.end_date and self.registration_type=='accepted':
            self.clean()
        super().save(*args, **kwargs)
    