from django.db import models
from user.models import Client 
from gym.models import Trainer, Branch, Shifts, Woman_Training_Hours
from classes.models import Class_Scheduel
from django.core.exceptions import ValidationError
from django.db.models import Q, UniqueConstraint
import datetime

today = datetime.datetime.now().date()
class TrainerGroups(models.Model):

    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='groups')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='groups')
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    group_capacity = models.PositiveIntegerField(default=0)
    days_off = models.JSONField(default=dict)
    is_deleted = models.BooleanField(default=False)
    
    def get_query(self):
        base_query = Q(
            start_hour__lte = self.start_hour,
            end_hour__gte = self.end_hour,
        ) |Q(
            start_hour__lte = self.start_hour,
            end_hour__gt = self.start_hour
        ) |Q(
            start_hour__lt = self.end_hour,
            end_hour__gte = self.end_hour
        )
        return base_query
    
    def check_trainer_gender(self):
        gender = self.trainer.employee.user.gender 
        query = self.get_query()
        query &= Q(
            gym=self.branch.gym
        )
        check = Woman_Training_Hours.objects.filter(query)
        if check.exists() and gender:
            for day in check:
                if day.day_of_week not in self.days_off.values():
                    raise ValidationError('as a male trainer you cant train groups in the hours you provide')
            
    def check_trainer_shift(self):
        gym_open_hour = self.branch.gym.start_hour
        gym_close_hour = self.branch.gym.close_hour
        gym_mid_day = self.branch.gym.mid_day_hour
        employee = self.trainer.employee
        shifts = Shifts.objects.filter(employee=employee)
        for shift in shifts:
            if shift.shift_type == 'Morning':
                
                if(gym_mid_day > self.start_hour >= gym_open_hour and self.start_hour < self.end_hour <= gym_mid_day):
                    pass 
                else:
                    raise ValidationError('invalid time added please check on the time entered and your shift')
                    
            
            elif shift.shift_type == 'Night':
                if(self.start_hour >= gym_mid_day or self.start_hour < gym_close_hour) \
                and (self.end_hour <= gym_close_hour or self.end_hour > gym_mid_day):
                    pass 
                else:
                    raise ValidationError('invalid time added please check on the time entered and your shift')
            
            elif shift.shift_type == 'FullTime':
                
                if(self.start_hour >= gym_open_hour or self.start_hour < gym_close_hour) \
                and (self.end_hour <= gym_close_hour or self.end_hour > gym_open_hour):
                    pass 
                else:
                    raise ValidationError('invalid time added please check on the time entered and your shift')
            for name in shift.days_off.values():
                if name not in self.days_off.values():
                    raise ValidationError('make sure that the trainer days off in the group days off')
            if shift.branch.gym != self.branch.gym:
                raise ValidationError('The selected trainer is not in the same gym as the group')
            
    def get_days_overlap_query(self):
        query = Q()
        for day, name in self.days_off.items():
            query|= ~Q(days_of_week__contains={f'{day}':name})
        return query
            
        
    def get_current_date(self):
        return datetime.datetime.now().date()
    
    def get_class_check_query(self):
        cuurent_date = self.get_current_date()
        days_query = self.get_days_overlap_query()
        query = (
                   Q(start_date__lte = cuurent_date, 
                    end_date__gte = cuurent_date,
            )|(
                Q(
                    start_time__lte = self.start_hour,
                    end_time__gt = self.start_hour
            )  |Q (
                    start_time__lt = self.end_hour,
                    end_time__gte = self.end_hour
            )  |Q (
                    start_time__gte = self.start_hour,
                    end_time__lte = self.end_hour
            )
        )|days_query
            )
        return query&Q(is_deleted = False, trainer = self.trainer)
    
    def get_trainer_classes(self):
        return Class_Scheduel.objects.filter(self.get_class_check_query())
                
    def check_trainer_classes(self):
        check_classes_overlap = self.get_trainer_classes()
        print(check_classes_overlap)
        if check_classes_overlap.exists():
            raise ValidationError('this trainer has class overlap with the entered data')
        
    def check_group_overlap(self):
        base_query = self.get_query()
        base_query &= Q(
            trainer=self.trainer
        )
        check_overlap = TrainerGroups.objects.filter(base_query).exclude(id=self.id)
        if check_overlap.exists():
            raise ValidationError('please check on the schedule there is an overlap')
    
    def clean(self) -> None:
        self.check_trainer_shift()
        self.check_group_overlap()
        self.check_trainer_gender()
        self.check_trainer_classes()
                
    def save(self,*args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    
    def check_delete(self):
        query = Q(
            trainer = self.trainer,
            start_date__lte = today,
            end_date__gte = today,
            registration_type = 'private',
            group = self.pk,
            is_deleted=False
        )
        clients =  Client_Trainer.objects.filter(query)
        if clients.exists():
            raise ValidationError('the group cannot be deleted because there is registered client in the group')
                
    def delete(self,*args, **kwargs):
        if self.is_deleted == False:
            self.check_delete()
            self.is_deleted = True
            self.save()
        
        
class Client_Trainer(models.Model):
    REGISTRATION_STATUS = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
    ]
    REGISTRATION_TYPES = [
        ('online', 'online'),
        ('private', 'private'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="TraineesRegistrations")
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name="TrainersRegistrations")
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)    
    registration_type = models.CharField(max_length=30,choices=REGISTRATION_TYPES) 
    registration_status = models.CharField(max_length=20,default='pending', choices=REGISTRATION_STATUS)
    rejection_reason = models.CharField(max_length=100, null=True)
    group = models.ForeignKey(TrainerGroups,on_delete=models.CASCADE, related_name="clients",null=True)
    created_at = models.DateField(auto_now_add=True)
    is_updated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    old_group_number  = models.IntegerField(null = True)
    