from django.db import models
from gym.models import Employee, Branch, Trainer
from user.models import Client

class Classes(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    registration_fee = models.FloatField(default=0.00)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='classes')
    is_deleted = models.BooleanField(default=False)
    image_path = models.ImageField(upload_to="images/", null=True)
    points = models.IntegerField(default=0)
    def delete(self):
        if self.is_deleted!= True:
            self.is_deleted = True
            self.save()
            
class Class_Scheduel(models.Model):
    class_id= models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='scheduel')
    start_time = models.TimeField(blank= True)
    end_time = models.TimeField(blank= True)
    trainer=models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='classes')
    days_of_week = models.JSONField(default=dict)
    start_date = models.DateField(blank= True)
    end_date = models.DateField(blank= True)
    hall = models.IntegerField(blank=True)    
    allowed_number_for_class = models.IntegerField(default=0)
    allowed_days_to_cancel = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    def delete(self):
        if self.is_deleted!= True:
            self.is_deleted = True
            self.save()
class Client_Class(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='classes')
    class_id = models.ForeignKey(Class_Scheduel, on_delete=models.CASCADE, related_name='clients')
    retieved_money = models.IntegerField(default=0)
    retrieved_reason = models.CharField(max_length=40)
    