from django.db import models
from django.contrib.auth.models import User 

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="client") 
    points = models.IntegerField(default=0)
    wakeup_time = models.TimeField(null = True)
    height = models.FloatField(default=0.0)
    app_rate = models.IntegerField(null = True)
    address = models.CharField(null = True)
        
    def delete(self, *args, **kwargs):
        if self.user:
            self.user.is_deleted = True
            self.user.save()
        # super(Client, self).delete(*args, **kwargs) delete the record

    