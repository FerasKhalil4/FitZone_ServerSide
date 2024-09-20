from django.db import models
from user.models import User
from django.db.models import UniqueConstraint

class BlockList(models.Model):
    blocker_id = models.ForeignKey(User,on_delete=models.CASCADE, related_name='blockings')
    blocked_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'blocked')
    blocked_at = models.DateTimeField(auto_now_add=True)
    blocking_status = models.BooleanField(default=True)
    
    
    def __str__(self):
        status = 'blocked' if self.blocking_status else 'unblocked'
        return f'{self.blocker_id.username} {status} {self.blocked_id.username} at {self.blocked_at}'
    
    def delete(self,*args, **kwargs):
        self.blocking_status = False
        self.save()