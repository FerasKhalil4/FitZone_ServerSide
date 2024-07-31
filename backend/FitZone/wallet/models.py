from django.db import models
from user.models import Client
from gym.models import Employee
class Wallet(models.Model):
    balance = models.PositiveIntegerField(default=0)
    client = models.OneToOneField(Client, on_delete=models.CASCADE,related_name='wallet')
    updated_at = models.DateTimeField(auto_now=True)

class Wallet_Deposit(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,related_name='walletDeposit')
    client = models.ForeignKey(Client, on_delete=models.CASCADE,related_name='depositWallet')
    amount  = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    