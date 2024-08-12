from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint

class UserChannel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='channels')
    channel_name = models.CharField(max_length=255)
    
class Chatroom(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_1')
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_2')
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['user_1', 'user_2'], name='unique_users')
        ]
        
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    is_seen = models.BooleanField(default=False)
    time = models.TimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)  
