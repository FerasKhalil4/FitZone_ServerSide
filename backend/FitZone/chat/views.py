from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import *
from drf_spectacular.utils import extend_schema
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q


class MessagesListAV(generics.ListAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    
    @extend_schema(
        summary='get messages'
    )
    def get(self, request, *args, **kwargs):
        try:
            chatroom = Chatroom.objects.get(pk=kwargs['chatroom_id'])
        except Chatroom.DoesNotExist:
            return Response({'error':'Chatroom does not exist'},status=status.HTTP_404_NOT_FOUND)
        
        Messages = Message.objects.filter(chatroom=chatroom.pk).order_by('date','time')
        unseen_messages = Messages.filter(~Q(user=request.user))
        unseen_messages.update(is_seen=True)
        
        data ={
            'type':'receiver_fun',
            'type_data':'message_seen',
        }
        
        sender = chatroom.user_1 if chatroom.user_2 == request.user.pk else chatroom.user_2
        
        channel = UserChannel.objects.get(user=sender.pk)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(channel.channel_name,data)
        
        return Response(MessageSerializer(Messages,many=True).data,status=status.HTTP_200_OK)
        
MessageList = MessagesListAV.as_view()


class ChatRoomsListAV(generics.ListAPIView):
    serializer_class = ChatroomSerializer
    queryset = Chatroom.objects.all()
    
    @extend_schema(
        summary='get chatrooms'
    )
    def get(self, request, *args, **kwargs):

        
        chatrooms = Chatroom.objects.filter(Q(user_1=request.user.pk) | Q(user_2=request.user.pk))
        data = ChatroomSerializer(chatrooms,many=True).data
        for room in data:
            if room['user_1'] == request.user.pk:
                room.pop('user_1', None) 
                room.pop('username_1', None) 
            else:
                room.pop('user_2', None)
                room.pop('username_2', None) 
                
        return Response(data,status=status.HTTP_200_OK)
chatroomsList = ChatRoomsListAV.as_view()