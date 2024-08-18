from channels.generic.websocket import WebsocketConsumer
from .models import Branch_Sessions
from chat.models import UserChannel
from user.models import Client
from plans.models import Gym_Training_plans,Training_plan,Client_Trianing_Plan,Gym_plans_Clients
from asgiref.sync import async_to_sync
from datetime import datetime


class GymConsumer(WebsocketConsumer):

    def connect(self):
        now = datetime.now().date()
        self.equipments = {}
        self.branch_id = self.scope.get('url_route').get('kwargs').get('branch_id')
        user = self.scope.get('user')
        
        try:
            self.client = Client.objects.get(user=user)
        except Client.DoesNotExist:
            return self.close(code=400)
        
        # session = Branch_Sessions.objects.create(
        #     branch = self.branch_id,
        #     client = self.client
        # )
        
        gym_training_plan = Gym_plans_Clients.objects.filter(client = self.client,start_date__lte = now, end_data__gte = now)
        print(gym_training_plan)
        private_training_plan = Client_Trianing_Plan.objects.filter(client = self.client,start_date__lte = now, end_data__gte = now)
        print(private_training_plan)
        try:
            user_channel = UserChannel.objects.get(user = user)
            user_channel.channel_name = self.channel_name
        except UserChannel.DoesNotExist:
            user_channel = UserChannel.objects.create(
                user = user,
                channel_name = self.channel_name
            )
        
        self.group_name = 'gym_session'
        
        async_to_sync(self.channel_layer.group_add) (
            self.group_name,
            user_channel.channel_name
        )
        print(self.channel_layer.groups)
        
        
        self.accept()
    def disconnect(self, code):
        
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, 
            self.channel_name)
        print(self.channel_layer.groups)
        
        return super().disconnect(code)
    
    def receive(self, text_data=None, bytes_data=None):
        ...
    
    def receiver_fun(self,data):
        ...
gym_consumer = GymConsumer.as_asgi()