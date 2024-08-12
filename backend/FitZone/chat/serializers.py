from rest_framework import serializers
from user.serializers import UserSerializer
from .models import *


class ChatroomSerializer(serializers.ModelSerializer):
    chatroom_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    username_1 = serializers.CharField(source='user_1.username',read_only=True)
    username_2 = serializers.CharField(source='user_2.username',read_only=True)
    
    class Meta:
        model = Chatroom
        fields = ['chatroom_id','created_at','user_1','user_2','username_1','username_2']
        
        

class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    username = serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model = Message
        fields = ['message_id', 'user','is_seen','time','date','message','chatroom','username']
        