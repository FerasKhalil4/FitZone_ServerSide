from .models import Saved_Posts
from rest_framework import serializers
from community.models import *
from community.serializers import *


class ClientPostsSerilizer(serializers.ModelSerializer):
    
    post_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    poster = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['post_id','poster','gym','content','reaction_count','comments_count','image','video','created_at']
        
    
    def get_poster(self,obj):
        try:
            if not obj.poster.is_trainer:
                return{ 
                       'name':obj.gym.name,
                       'image':obj.gym.image_path  if ((len(str(obj.gym.image_path)) > 0)) else None
                }
            else:
                return {
                    'name':obj.poster.user.username,
                    'image':None
                        }
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    
    def get_image(self,obj):
        return Image.objects.filter(post=obj.pk).values_list('image',flat=True)
    
    def get_video(self,obj):
        return Video.objects.filter(post=obj.pk).values_list('video',flat=True)
    
    def to_representation(self, instance):
        
        data = super().to_representation(instance)
        user = self.context.get('request').user
        try:
            check = Saved_Posts.objects.get(client__user=user, post=data['post_id'])
            data['is_saved'] = True
        except Saved_Posts.DoesNotExist:
            pass
        
        return data

class CommentRepliesSerializer(serializers.ModelSerializer):
    client = serializers.CharField(source='client.user.username')
    
    class Meta:
        model = Comments_Replies
        fields =['client','comment','created_at']
        
class SavedPostsSerializer(serializers.ModelSerializer):
    posts = ClientPostsSerilizer(source='post')
    class Meta:
        model = Saved_Posts
        fields = ['posts','created_at']