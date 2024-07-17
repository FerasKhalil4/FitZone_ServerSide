from django.db import models
from user.models import User
class Points(models.Model):
    user = models.ForeignKey(User,on_delete = models.SET_NULL,related_name="points", null=True)
    activity = models.CharField(max_length=50)
    points = models.PositiveIntegerField(default=0,null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    points_percentage = models.PositiveIntegerField(null=True)
    def __str__(self):
        return self.activity