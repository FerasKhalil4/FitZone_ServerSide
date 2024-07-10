from rest_framework import serializers
from .models import *

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['video']
        
class LikesSerializer(serializers.ModelSerializer):
    clients = serializers.ReadOnlyField(read_only=True, source ='clients.user.username')
    class Meta:
        model = likes
        fields = ['clients']
        ordering =['created_ata']
        
class CommentsSerializer(serializers.ModelSerializer):
    clients = serializers.ReadOnlyField(read_only=True, source ='clients.user.username')
    class Meta:
        model = Comments
        fields = ['comments','clients']
        ordering =['created_ata']
        
        
class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(read_only=True,many=True,required=False)
    videos = VideoSerializer(read_only=True,many=True,required=False)
    likes= LikesSerializer(many=True,read_only=True)
    comments = CommentsSerializer(many=True,read_only=True)
    poster_id = serializers.IntegerField(write_only=True)
    poster=serializers.ReadOnlyField(read_only=True, source='poster.user.username')
    gym_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Post
        fields = ['approved_by','id','gym_id','images','videos','content','like_count','likes','comments','poster','is_approved','poster_id','created_at']
        ordering = ['created_at']
        

        