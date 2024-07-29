from django.db import models
from user.models import Client

class Wallet(models.Model):
    amount = models.PositiveIntegerField(default=0)
    client = models.OneToOneField(Client, on_delete=models.CASCADE,related_name='wallet')
    updated_at = models.DateTimeField(auto_now=True)
    