from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from .serializers import MessageSerializer,ChatroomSerializer
from rest_framework.response import Response
from .models import Chatroom,UserChannel,Message
from user.models import User
import json 
from django.db.models import Q
from asgiref.sync import async_to_sync


class BaseChatConsumer(WebsocketConsumer):
    
    def receive(self, text_data=None ,bytes_data=None):
        try:           
            text_data = json.loads(text_data)
        except  Exception as e:
            print(f"{e}")
            self.disconnect(code=1001)
            raise StopConsumer()
        text_type = text_data.pop('type', None)
        
        print(text_data)
        if text_type == 'new_message':
            try:
                text_data['user'] = self.scope.get('user').pk
                text_data['chatroom'] = self.chatroom.pk
                message_serializer = MessageSerializer(data=text_data)
                message_serializer.is_valid(raise_exception=True)
                message_serializer.save()
                
                data = {
                    'type':'receiver_fun',
                    'message': message_serializer.data['message']
                }
                try:
                    
                    receiver_channel = UserChannel.objects.get(user=self.receiver)
                    async_to_sync(self.channel_layer.send)(receiver_channel.channel_name, data)
                    
                except UserChannel.DoesNotExist:
                    pass 
                
            except Exception as e:
                print(str(e))
                self.disconnect(code=1001)
                raise StopConsumer()
        elif text_type == 'message_seen':
            try:
                query =Q(
                    chatroom=self.chatroom,
                    is_seen=False,
                )&~ Q(
                  user = self.scope.get('user')
                )
                message = Message.objects.filter(query)
                print(message)
                sender_channel = UserChannel.objects.get(user=self.receiver)

                message.update(is_seen=True)
                
                data = {
                    'type':'receiver_fun',
                    'type_data':'is_seen'
                }
                
                async_to_sync(self.channel_layer.send)(sender_channel.channel_name, data)
                
            except Exception as e:
                print(str(e))
                self.disconnect(code=1001)
                raise StopConsumer()
        
    
    def receiver_fun(self, data):
        print(data)
        self.send(json.dumps(data))

class NewChatConsumer(BaseChatConsumer):
    
    def connect(self):
        try:
            data = {}
            
            self.receiver = self.scope.get('url_route').get('kwargs').get('user_id')
            data['user_1'] = self.scope.get('user').pk
            data['user_2'] = self.receiver 
            
            chat_serializer = ChatroomSerializer(data=data)
            chat_serializer.is_valid(raise_exception=True)
            self.chatroom = chat_serializer.save()
            
            self.accept()
            
            try:
                channel = UserChannel.objects.get(user=self.scope.get('user'))
                channel.channel_name = self.channel_name
                channel.save()
            except UserChannel.DoesNotExist:
                channel = UserChannel.objects.create(user=self.scope.get('user'), channel_name=self.channel_name)
                
                
        except Exception as e:
            print(str(e))

            
        
    def receive(self,text_data):
        super().receive(text_data)
        
                     
    def receiver_fun(self, data):
        super().receiver_fun(data)

NewChat = NewChatConsumer.as_asgi()


class OldChatConsumer(BaseChatConsumer):
    def connect(self):
        try:
            chatroom_id = self.scope.get('url_route').get('kwargs').get('chatroom_id')
            self.chatroom = Chatroom.objects.get(pk=chatroom_id)
            print(self.chatroom.user_1.pk)
            print(self.chatroom.user_2.pk)
            print(self.scope.get('user').pk)
            self.receiver = None
            
            if self.chatroom.user_2 == self.scope.get('user'):
                self.receiver = self.chatroom.user_1
            elif self.chatroom.user_1 == self.scope.get('user'):
                self.receiver = self.chatroom.user_2
            else:
                print('User not authorized to join this chatroom')
                self.disconnect(code=1000)
                raise StopConsumer()  
            self.accept()       
                
            
            try:
                channel = UserChannel.objects.get(user=self.scope.get('user'))
                channel.channel_name = self.channel_name
                channel.save()
            except UserChannel.DoesNotExist:
                channel = UserChannel.objects.create(user=self.scope.get('user'), channel_name=self.channel_name)
        except Chatroom.DoesNotExist:
            print(f'Chatroom with ID {chatroom_id} does not exist')
            self.disconnect(code=1001) 
            raise StopConsumer()
        

    def receive(self, text_data):
        super().receive(text_data)

    def receiver_fun(self, data):
        print('subclass receiver_fun')
        super().receiver_fun(data)
OldChat = OldChatConsumer.as_asgi()