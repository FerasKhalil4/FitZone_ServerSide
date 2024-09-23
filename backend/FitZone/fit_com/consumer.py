from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from community.models import Comments,Reactions,Post
from user.models import Client
from chat.models import UserChannel
from .models import Saved_Posts
from .services import PostIntercationsService
import json

class CommunityConsumer(WebsocketConsumer):
    
    def connect(self):
        
        try:
            self.user_channel = UserChannel.objects.get(user=self.scope.get('user'))
            self.user_channel.channel_name = self.channel_name
            self.user_channel.save()
            
        except UserChannel.DoesNotExist:
            self.user_channel = UserChannel.objects.create(user=self.scope.get('user'),chnnel_name = self.channel_name)
        return super().connect()
    
    def receive(self, text_data=None, bytes_data=None):
        
        text_data = json.loads(text_data)
        type = text_data.pop('type')
        client = Client.objects.get(user=self.scope.get('user').pk)
        post = Post.objects.get(pk=text_data['post_id'])
        data = {
            'type': 'receive_fun',
            'post_id':text_data['post_id']
        }
        
        if type == 'reaction':
            reaction = PostIntercationsService.handle_reaction(post,text_data['reaction'],client)
            data['reaction'] = reaction.reaction 
            data['total_reactions'] = reaction.post.reaction_count
        
        elif type == 'comment':
            comment = PostIntercationsService.handle_comments(post,text_data['comment'],client)
            data['comment'] = comment.comment
            data['total_comments'] = comment.post.comments_count
            
        elif type == 'reply':
            reply = PostIntercationsService.handle_reply(post,text_data['comment'],text_data['reply'],client)
            data['reply'] = reply
            data['comment'] = text_data['comment']
            
        elif type == 'delete_comment':
                message = PostIntercationsService.handle_delete_comment(post,text_data['comment'],client)
                data['message'] = message
                
        elif type == 'deleted_reply':
            message = PostIntercationsService.handle_deleted_reply(post,text_data['reply'])
            data['message'] = message
        
        elif type == 'save_post':
            message = PostIntercationsService.save_post(post,client)
            data['message'] = message

        elif type == 'unsave_post':
            message = PostIntercationsService.unsave_post(post,client)
            data['message'] = message
                
        async_to_sync(self.channel_layer.send)(self.channel_name,data)
        
        return super().receive(text_data, bytes_data)
    
    def disconnect(self, code):
        return super().disconnect(code)
    
    def receive_fun(self, data):
        self.send(json.dumps(data))
    
community = CommunityConsumer.as_asgi()