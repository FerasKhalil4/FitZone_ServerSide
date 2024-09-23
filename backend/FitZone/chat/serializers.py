from rest_framework import serializers
from user.serializers import UserSerializer
from .models import *
from block.models import BlockList
from django.db.models import Q
from gym.models import Trainer


class ChatroomSerializer(serializers.ModelSerializer):
    chatroom_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    username_1 = serializers.CharField(source='user_1.username',read_only=True)
    username_2 = serializers.CharField(source='user_2.username',read_only=True)
    
    class Meta:
        model = Chatroom
        fields = ['chatroom_id','created_at','user_1','user_2','username_1','username_2']
        
    
    def update_represented_data(self,representation,number):
            representation['is_block'] = True
            representation[f'username_{number}'] = 'Annonymous'
            representation[f'user_{number}'] = None
            return representation
                
    def check_block(self,representation,array):
        print(array)
        
        for id in array:
            
            if representation['user_1']  == id:
                self.update_represented_data(representation,1)
                
            elif representation['user_2']  == id:
                self.update_represented_data(representation,2)
                
        return representation
        
        
    def to_representation(self, instance):
        try:
            representation =  super().to_representation(instance)
            request = self.context.get('request')
            block_query = Q(Q(
            blocker = request.user,
            )|Q(
                blocked = request.user,
            )) & Q(
                blocking_status = True
            )
            blocked_users_queryset = BlockList.objects.filter(block_query)
            blocked_users = [item.blocked.pk for item in blocked_users_queryset]
            blocking_users = [item.blocker.pk for item in blocked_users_queryset]

            representation = self.check_block(representation, blocked_users)
            representation = self.check_block(representation, blocking_users)
            
            return representation
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    
        
        

class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    username = serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model = Message
        fields = ['message_id', 'user','is_seen','time','date','message','chatroom','username']
        