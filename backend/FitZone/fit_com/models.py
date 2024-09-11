from django.db import models
from community.models import Post, Comments
from user.models import Client

class Saved_Posts(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='SavedPosts')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='SavedPosts')
    created_at = models.DateTimeField(auto_now_add=True)
    unsaved = models.BooleanField(default=False)
    
    def delete(self, *args, **kwargs):
        if not self.unsaved:
            self.unsaved = True
            self.save()
            
    
class Comments_Replies(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reply')
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE,related_name='reply')
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)



    
    