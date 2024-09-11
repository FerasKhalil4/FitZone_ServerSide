from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, CheckConstraint
from django.core.exceptions import ValidationError
from user.models import Client
from gym.models import Branch,Trainer,Gym

class Rate(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='rates')
    value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_app_rate = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def check_available_rating(self):
        if self.is_app_rate:
            
            check = Rate.objects.filter(
                client=self.client,
                is_app_rate=True,
                is_deleted=False
            ).exclude(id=self.pk)

            if check.exists():
                raise ValidationError('this client already rated the app if you wanted to change it go ahead and update it' )
    
    def clean(self):
        super().clean()
        self.check_available_rating()
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
                
        

class GymRate(models.Model):
    rate = models.OneToOneField(Rate, on_delete=models.CASCADE, related_name='gym_rate')
    gym = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='ratings')
    
    def check_available_rating(self)->None:
        check = GymRate.objects.filter(
            rate__client = self.rate.client,
            rate__is_deleted = False,
            gym__is_active= True,
            gym = self.gym
        )
        
        if check.exists():
            raise ValidationError('this client already rated this gym if you wanted to change it go ahead and update it')
        
    
    def clean(self):
        super().clean()
        if self.rate.is_app_rate:
            raise ValidationError('App rate cannot be given for gym')
        self.check_available_rating()
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        
    
class TrainerRate(models.Model):
    rate = models.OneToOneField(Rate, on_delete=models.CASCADE, related_name='trainer_rate')
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='ratings')
    
    def check_available_rating(self)->None:
        check = TrainerRate.objects.filter(
            rate__client = self.rate.client,
            rate__is_deleted = False,
            trainer = self.trainer
        )
        if check.exists():
            raise ValidationError('this client already rated this trainer if you wanted to change it go ahead and update it')
    
    def clean(self):
        super().clean()
        if self.rate.is_app_rate:
            raise ValidationError('App rate cannot be given for trainer')
        self.check_available_rating()
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        
class Feedback(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'low'),
        ('moderate', 'moderate'),
        ('high', 'high'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='feedback', null=True)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, null=True)