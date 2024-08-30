from django.db import models
from user.models import Client
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.core.exceptions import ValidationError
import secrets
import string
class Voucher(models.Model):
    name = models.CharField(max_length=50, blank=True)
    points_required = models.IntegerField(default=0)
    number_of_days = models.IntegerField()
    restrict_num_using = models.PositiveIntegerField(null=True)
    is_deleted = models.BooleanField(default=False)
    discount = models.PositiveIntegerField()
    
    def delete(self,obj):
        if obj.is_deleted == False:
            obj.is_deleted = True
            obj.save()
            
class Redeem(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='redeem')
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='redeem')
    start_date = models.DateField(auto_now_add=True)
    expired_date = models.DateField(null=True)
    times_used = models.PositiveIntegerField(default=0)
    points_used = models.PositiveIntegerField()
    code = models.CharField()
    
    
    def check_code(self,code):
        now = self.now

        check_old_code = Redeem.objects.filter(code=code,expired_date__lt=now,client=self.client)
        
        if check_old_code.exists():
            check_old_code.update(code='used') 
            return True
        
        overlapped_query = Q(
            start_date__lte = now,
            expired_date__gt=now,
        )|Q(
            start_date__lt =self.expired_date,
            expired_date__gte=self.expired_date,
        )|Q(
            start_date__gte = now,
            expired_date__lte=self.expired_date,
        )
        
        query = overlapped_query &Q(
            code=code,
            client=self.client
        )
        return not Redeem.objects.filter(query).exists()
    
    def create_random(self,length):
        characters = string.ascii_letters + string.digits
        check = False
        while check == False:
            
            code = ''.join(secrets.choice(characters) for _ in range(length))
            check = self.check_code(code)
        
        return code
    
    
    def check_client_points(self):
        
        if self.client.points < self.voucher.points_required:
            raise ValidationError('Client does not have enough points')
        self.client.points -= self.voucher.points_required
        self.client.save()
    
    def clean(self):
        super().clean()
        self.check_client_points()
    
        
    def save(self, *args, **kwargs):
        self.clean()
        if not self:
            if self.expired_date is None:
                self.now = datetime.now().date()
                self.expired_date = self.now + relativedelta(days=self.voucher.number_of_days)
            self.code = self.create_random(10)
            self.points_used = self.voucher.points_required
        
        super(Redeem, self).save(*args, **kwargs)
    