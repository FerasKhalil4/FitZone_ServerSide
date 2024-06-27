from django.db import models

class Gym(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=100)
    address = models.CharField(max_length=50)
    start_hour = models.TimeField()
    closing_hour = models.TimeField()
    has_store = models.BooleanField(default=False)
    regestration_price = models.FloatField()
    image_path = models.ImageField(upload_to='images/' , null= True)
    created_at = models.DateTimeField(auto_now_add=True)
    allow_retrival = models.BooleanField(default=False)
    duration_allowed = models.IntegerField(null = True)
    cut_percentage = models.FloatField(null = True)
    