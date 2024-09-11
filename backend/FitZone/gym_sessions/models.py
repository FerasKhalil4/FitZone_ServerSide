from django.db import models
from .services import SubscriptionService
from user.models import Client
from gym.models import Branch, Registration_Fee
from points.models import Points
from plans.models import Gym_plans_Clients
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db.models import Q
import datetime
import math

now = datetime.datetime.now().date()

class Gym_Subscription(models.Model):
    
    client = models.ForeignKey(Client,on_delete=models.CASCADE,related_name='gym_sessions')
    branch = models.ForeignKey(Branch,on_delete=models.CASCADE,related_name='clients')
    registration_type = models.ForeignKey(Registration_Fee,on_delete=models.CASCADE,related_name = 'clients_registration')
    start_date = models.DateField(auto_now=True)
    end_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    update_at = models.DateTimeField(auto_now=True)
    price_offer = models.FloatField(null=True)
    
    def get_product_points(self):
        Purchasing_points = Points.objects.get(activity="Purchasing").points_percentage
        first_time_points = Points.objects.get(activity="First Time Activity").points
        check = Gym_Subscription.objects.filter(client=self.client)
        print(first_time_points)
        points = math.ceil(self.registration_type.fee / Purchasing_points) if Purchasing_points != 0 else 0
        
        if check.exists():
            pass
        else: 
            points += first_time_points 
            
        return  points
    
    def check_registration_overlap(self)->None:
        print(self.client)
        check = Gym_Subscription.objects.filter(client=self.client,start_date__lte=now,end_date__gte=now,is_active=True,branch=self.branch).exclude(id = self.id)
        print(check)
        if check.exists():
            raise ValidationError('Client is already registered in this branch')
        
    def check_gym_capacity(self):
        if (self.branch.gym.is_deleted == False) and (self.branch.is_active == True):
            if self.branch.number_of_clients_allowed < (self.branch.current_number_of_clients + 1):
                raise ValidationError('you cant register in this branch where it is full')
        else:
            raise ValidationError('gym is deleted')
        
    def check_registration_branch(self):
        if not self.branch.gym == self.registration_type.gym :
            raise ValidationError('Registration type must be for the same gym')
    
    def check_client_gym_trianing_plan(self):
        query = Q(
            client=self.client, 
            start_date__lte = now,
            end_date__gte = now,
            is_active=True,
        ) & ~Q(
            gym_training_plan__gym = self.branch.gym.pk
        )
        check = Gym_plans_Clients.objects.filter(query)
        check.update(is_active=False)
        
               
    def check_registration_client_balance(self,points):
        
        if self.price_offer is None:
            fee = self.registration_type.fee
        else:
            fee = self.price_offer
        
        if self.pk is None:
            self.branch.current_number_of_clients += 1
            self.branch.save()
            SubscriptionService.check_client_balance(self.client,fee,'cut')
            SubscriptionService.client_points(self.client,points)
            
        else:
            instance = Gym_Subscription.objects.get(pk=self.pk)
            print('update')
            try:
                if instance.price_offer is None:
                    print('instance has no  previous offer')
                    old_fee = Registration_Fee.objects.get(id=instance.registration_type, gym=self.branch.gym.pk).fee
                else:
                    print('instance has previous offer')
                    old_fee = instance.price_offer
            except Registration_Fee.DoesNotExist:
                raise ValidationError ('registration type does not exist')
            
            if self.allowed_date < now:            
                print('allowed durations for update is not available')
                if old_fee > fee :
                    print('new fee is less then the existed fee')
                    raise ValidationError('you cant change the registration type to this type')
                elif old_fee < fee :
                    print('new fee is more or equal to the existed fee')
                    
                    new_fee = fee - old_fee
                    SubscriptionService.check_client_balance(self.client,new_fee,'cut')
                    SubscriptionService.client_points(self.client,points)
                    
            else:
                print('allowed durations for update is available')
                if old_fee < fee :
                    print('new fee is more then the existed fee')
                    new_fee = fee - old_fee
                    SubscriptionService.check_client_balance(self.client,new_fee,'cut')    
                    SubscriptionService.client_points(self.client,points)
                    
                elif fee < old_fee :
                    print('new fee is more or equal to the existed fee')
                    if self.branch.gym.cut_percentage is not None:
                        new_fee = old_fee - fee
                        SubscriptionService.check_client_balance(self.client,new_fee,'add')
                        
                        
                        
                        
    def allow_cancel(self) -> None:
        points = self.get_product_points()
        if self.branch.gym.allowed_days_for_registraiton_cancellation != 0:
            print('check if the gym allows cancellation')
            self.allowed_date= now + relativedelta(days=self.branch.gym.allowed_days_for_registraiton_cancellation)
            
            if now > self.allowed_date:
                print('allowed days for cancellation are  not available')
                
                raise ValidationError('you cannot cancel your gym membership')
            else:
                print('allowed days for cancellation are available')
                
                self.is_active = False
                self.save()
                self.branch.current_number_of_clients -= 1
                self.branch.save()
                
                if self.branch.gym.cut_percentage is not None:
                    
                    print('check if the gym allows to retrieve money')
                    fee = self.registration_type.fee
                    retrieved_value = fee * (self.branch.gym.cut_percentage / 100)  
                    SubscriptionService.check_client_balance(self.client,retrieved_value,'add')  
                SubscriptionService.client_points(self.client,points,flag=True)

                    
                                         

    def clean(self)->None:
        super().clean()
        self.allowed_date= now + relativedelta(days=self.branch.gym.allowed_days_for_registraiton_cancellation)
        points = self.get_product_points()
        print('check')
        
        self.check_gym_capacity()
        print('check')
        
        self.check_registration_branch()
        print('check')
        
        self.check_registration_overlap()
        print('check')
        
        self.check_client_gym_trianing_plan()
        print('check')
        
        self.check_registration_client_balance(points)
        print('check')
        
        
    def create_end_date(self):
        durarion_mapping = {
            '1_day':relativedelta(days=1),
            '15_days':relativedelta(days=15),
            'monthly':relativedelta(months=1),
            '3_months':relativedelta(months=3),
            '6_months':relativedelta(months=6),
            'yearly':relativedelta(years=1),
        }
        delta = durarion_mapping[self.registration_type.type]
        if delta:

            self.end_date = now + delta
        else: 
            raise ValidationError('registration type is not supported')
        

            
    def save(self,*args, **kwargs):
        print('check')
        
        self.clean()
        self.create_end_date()
        return super().save(*args, **kwargs)    
    
    def delete(self, *args, **kwargs):
        if self:
            print('delete')
            self.allow_cancel()
            
class Branch_Sessions(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sessions') 
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='clients_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_points(self):
        print('get session points')
        points = Points.objects.get(activity = 'Gym Sessions Points').points
        SubscriptionService.client_points(self.client,points)
        
    def check_time(self):
        print('check time')
        if not Branch_Sessions.objects.filter(client=self.client,branch=self.branch,created_at__date = datetime.datetime.now().date()).exclude(id=self.id).exists():
            print('add_points')
            self.get_points()
        else:
            print('check failed')
            pass 
            
    def clean(self) -> None:
        super().clean()
        self.check_time()
        
    def save(self,*args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
    