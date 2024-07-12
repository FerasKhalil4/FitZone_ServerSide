from django.db import models
from user.models import User

class Gym(models.Model):
    name = models.CharField(max_length=30 , unique=True)
    description = models.TextField(max_length=100 , null = True)
    regestration_price = models.FloatField()
    image_path = models.ImageField(upload_to='images/' , null= True)
    created_at = models.DateTimeField(auto_now_add=True)
    allow_retrival = models.BooleanField(default=False)
    duration_allowed = models.IntegerField(null = True)
    cut_percentage = models.FloatField(null = True)
    is_deleted = models.BooleanField(default=False)
    start_hour = models.TimeField()
    close_hour = models.TimeField()
    mid_day_hour = models.TimeField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manager')
    allow_public_posts = models.BooleanField(default=True)
    allow_public_products = models.BooleanField(default=True)
    
    
class Woman_Training_Hours(models.Model):
    gym = models.ForeignKey(Gym , on_delete=models.CASCADE,related_name="woman_gym" )
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    day_of_week = models.CharField()
    
    
    
    
class Branch(models.Model):
    gym = models.ForeignKey(Gym , on_delete=models.CASCADE,related_name="gym" )
    address = models.CharField(max_length=50)
    has_store = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def delete(self , *args , **kwargs):
        if self:
            self.is_active = False
            self.save()
    

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="user") 
    is_trainer = models.BooleanField(default=False)
    start_date = models.DateField()
    quit_date = models.DateField(null=True)
    
    
class Shifts (models.Model):
    employee = models.ForeignKey(Employee , on_delete=models.CASCADE, related_name="employee")
    branch = models.ForeignKey(Branch , on_delete=models.CASCADE,related_name="branch")
    shift_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    days_off = models.JSONField(default = dict)