from django.db import models
from user.models import User
from django.db.models import UniqueConstraint

class Gym(models.Model):
    name = models.CharField(max_length=30 , unique=True)
    description = models.TextField(max_length=100 , null = True)
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
    allowed_days_for_registraiton_cancellation = models.IntegerField(default=0)
    number_of_clients_allowed = models.IntegerField(default=0)
    current_number_of_clients= models.IntegerField(default=0)
    def __str__(self) -> str:
        return f"{self.id}:{self.name}"
    
class Registration_Fee(models.Model):
    gym = models.ForeignKey(Gym , on_delete=models.CASCADE,related_name="fees" )
    type = models.CharField(max_length=50)
    fee = models.FloatField(default = 0.0)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=('gym','type'), name='gym_type'),
        ]
    
class Woman_Training_Hours(models.Model):
    gym = models.ForeignKey(Gym , on_delete=models.CASCADE,related_name="woman_gym" )
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    day_of_week = models.CharField()
    
class Branch(models.Model):
    gym = models.ForeignKey(Gym , on_delete=models.CASCADE,related_name="gym" )
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50, blank = True)
    street = models.CharField(max_length=50,blank = True)
    has_store = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def delete(self , *args , **kwargs):
        if self:
            self.is_active = False
            self.save()
    
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="user") 
    is_trainer = models.BooleanField(default=False)

class Trainer(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="trainer")
    num_of_trainees = models.IntegerField(default=0)
    allow_public_posts = models.BooleanField(default=True)
    session_period = models.IntegerField(default=0)
    private_training_price = models.FloatField(default=0.00)
    online_training_price = models.FloatField(default=0.00)
    

    
class Shifts (models.Model):
    employee = models.ForeignKey(Employee , on_delete=models.CASCADE, related_name="employee")
    branch = models.ForeignKey(Branch , on_delete=models.CASCADE,related_name="branch")
    shift_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    days_off = models.JSONField(default = dict)
    

    