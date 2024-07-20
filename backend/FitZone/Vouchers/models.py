from typing import Any
from django.db import models

class Voucher(models.Model):
    name = models.CharField(max_length=50, blank=True)
    points_required = models.IntegerField(default=0)
    number_of_days = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    
    def delete(self,obj):
        if obj.is_deleted == False:
            obj.is_deleted = True
            obj.save()