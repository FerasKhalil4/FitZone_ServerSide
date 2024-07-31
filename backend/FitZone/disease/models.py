from django.db import models
from equipments.models import Equipment
from user.models import Client
from django.db.models import UniqueConstraint

class Disease(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=100)
    
class Limitations(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="disease")
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name="equipment")
    class Meta:
        constraints = [
            UniqueConstraint(fields=['equipment', 'disease'], name='unique_equipment_disease')
        ]
    
class Client_Disease(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='disease')
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='clients')
    
    def __str__(self):
        return f'{self.client.user.username}:{self.disease.name}'

    class Meta:
        constraints = [
            UniqueConstraint(fields=['client', 'disease'], name='unique_client_disease')
        ]
    