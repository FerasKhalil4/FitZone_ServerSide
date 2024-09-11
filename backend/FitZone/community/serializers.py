from rest_framework import serializers
from .models import *
from fit_com.models import Comments_Replies
from fit_com.serializers import CommentRepliesSerializer
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['video']
        
class ReactionsSerializer(serializers.ModelSerializer):
    clients = serializers.CharField( source ='client.user.username',read_only=True)
    class Meta:
        model = Reactions
        fields = ['pk','clients','reaction','created_at']
        ordering =['created_at']
        
class CommentsSerializer(serializers.ModelSerializer):
    clients = serializers.CharField( source ='client.user.username',read_only=True)
    reply = serializers.SerializerMethodField()
    class Meta:
        model = Comments
        fields = ['pk','comment','clients','created_at','reply']
        ordering =['created_at']
        
        
    def get_reply(self,obj):
        reply = Comments_Replies.objects.filter(comment=obj.pk,is_deleted=False)
        data = CommentRepliesSerializer(reply,many=True).data
        return data
    def to_representation(self, instance):
        
        user = self.context.get('request').user.username
        data = super().to_representation(instance)
        
        if data['clients'] == user:
            data['allow_delete'] = True
        for item in data['reply']:
            if item['client'] == user:
                item['allow_delete'] = True
        return data
            
        
        
class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(read_only=True,many=True,required=False)
    videos = VideoSerializer(read_only=True,many=True,required=False)
    reactions= ReactionsSerializer(many=True,read_only=True)
    comments = CommentsSerializer(many=True,read_only=True)
    poster_id = serializers.IntegerField(write_only=True)
    poster=serializers.ReadOnlyField(read_only=True, source='poster.user.username')
    gym_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Post
        fields = ['approved_by','id','gym_id','images','videos','content','reaction_count','comments_count','reactions','comments','poster','is_approved','poster_id','created_at']
        ordering = ['created_at']
        

        