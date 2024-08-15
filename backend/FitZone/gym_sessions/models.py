from django.db import models
from .services import SubscriptionService
from user.models import Client
from gym.models import Branch, Registration_Fee
from wallet.models import Wallet, Wallet_Deposit
from offers.models import Percentage_offer, ObjectHasPriceOffer
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db.models import Q
import datetime

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
    
    
    def check_registration_overlap(self)->None:
        check = Gym_Subscription.objects.filter(client=self.client,start_date__lte=now,end_date__gte=now,is_active=True).exclude(id = self.id)
        if check.exists():
            raise ValidationError('Client is already registered')
        
    def check_gym_capacity(self):
        if (self.branch.gym.is_deleted == False) and (self.branch.is_active == True):
            if self.branch.number_of_clients_allowed < (self.branch.current_number_of_clients + 1):
                raise ValidationError('you cant register in this branch where it is full')
        else:
            raise ValidationError('gym is deleted')
        
    def check_registration_branch(self):
        if not self.branch.gym == self.registration_type.gym :
            raise ValidationError('Registration type must be for the same gym')
            
    def check_registration_client_balance(self):
        
        if self.price_offer is None:
            fee = self.registration_type.fee
        else:
            fee = self.price_offer
        
        if self.pk is None:
            
            SubscriptionService.check_client_balance(self.client,fee,'cut')
            
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
                    
            else:
                print('allowed durations for update is available')
                if old_fee < fee :
                    print('new fee is more then the existed fee')
                    new_fee = fee - old_fee
                    SubscriptionService.check_client_balance(self.client,new_fee,'cut')    
                elif fee < old_fee :
                    print('new fee is more or equal to the existed fee')
                    if self.branch.gym.cut_percentage is not None:
                        new_fee = old_fee - fee
                        SubscriptionService.check_client_balance(self.client,new_fee,'add')
                        
                        
    def allow_cancel(self) -> None:
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
                if self.branch.gym.cut_percentage is not None:
                    print('check if the gym allows to retrieve money')
                    fee = self.registration_type.fee
                    retrieved_value = fee * (self.branch.gym.cut_percentage / 100)  
                    SubscriptionService.check_client_balance(self.client,retrieved_value,'add')  
                                         

    def clean(self)->None:
        super().clean()
        self.allowed_date= now + relativedelta(days=self.branch.gym.allowed_days_for_registraiton_cancellation)
        self.check_gym_capacity()
        self.check_registration_branch()
        self.check_registration_overlap()
        self.check_registration_client_balance()
        
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
    