from django.db import models
from gym.models import Employee , Gym
from user.models import Client
class Post(models.Model):
    poster = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="poster")
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE,related_name="post")
    content = models.TextField(blank=True, null=True)
    like_count = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(Employee,on_delete=models.CASCADE, related_name="approved",null = True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def delete(self):
        self.is_deleted = True
        self.save()

class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="images/", blank=True)

class Video(models.Model):
    post = models.ForeignKey(Post , on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='videos/')
    
class likes(models.Model):
    post = models.ForeignKey(Post , on_delete=models.CASCADE, related_name='likes')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

class Comments(models.Model):
    post = models.ForeignKey(Post , on_delete=models.CASCADE, related_name='comments')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)