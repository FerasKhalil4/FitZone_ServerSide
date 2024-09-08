from django.db import models

# Create your models here.

class Food(models.Model):
    name = models.CharField(max_length=50)
    bf = models.IntegerField()
    lu = models.IntegerField()
    di = models.IntegerField()
    cal = models.IntegerField()
    fat = models.FloatField()
    pro = models.FloatField()
    sug = models.FloatField()
    imagepath= models.CharField(default="",max_length=100)

