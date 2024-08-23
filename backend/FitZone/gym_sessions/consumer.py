from channels.generic.websocket import WebsocketConsumer
from chat.models import UserChannel
from user.models import Client
from plans.models import Workout_Exercises
from equipments.models import Diagrams_Equipments
from asgiref.sync import async_to_sync
import json
import threading

class Gym_Session_Mixin():
    
    @staticmethod
    def get_check(type_):
        return {
            'Cardio':1,
            'Equipment':3,
            'Free-Weights':None,
        }.get(type_)
        
    @staticmethod
    def use_equipment(branches, branch_id, text_data, username, data, check):
        equipment_id = text_data['equipment']
        events = branches[branch_id]['events']
        
        events[equipment_id].append(username)

        data['event'] = {
                        'equipment':equipment_id,
                        'action':'start exercise',
                        'current_users':events[equipment_id]
                         }
        
        if len(events[equipment_id]) == check:
            data['event']['status'] = 'unavilable'
        
        return data


    @staticmethod
    def get_tracked_equipment(workout_id, user, users, branch_id, branches):
        
        branch = branches[branch_id]
        exercises = Workout_Exercises.objects.filter(workout=workout_id).order_by('order')
        
        for exercise in exercises:
            
            branch_equipment = Diagrams_Equipments.objects.filter(diagram__branch = branch_id
                                                                , equipment = exercise.exercise.equipment.pk,status=True,is_deleted=False).values_list('pk', flat=True)
            
            users[user.pk]['current_order'] = -1
            users[user.pk]['excercises'].append(exercise.exercise.pk)
            
            if exercise.exercise.pk not in branch['excercises']:
                branch['excercises'][exercise.exercise.pk] = []
                for equipment in branch_equipment:
                    branch['excercises'][exercise.exercise.pk].append(equipment)
            else:
                for equipment in branch_equipment:
                    if equipment not in branch['excercises'][exercise.exercise.pk]:
                        branch['excercises'][exercise.exercise].append(equipment)

    @staticmethod
    def get_user_channel(user, channel_name):
        
        try:
            user_channel = UserChannel.objects.get(user = user)
            user_channel.channel_name = channel_name
            user_channel.save()
            
        except UserChannel.DoesNotExist:
            user_channel = UserChannel.objects.create(
                user = user,
                channel_name = channel_name
            )
        return user_channel

class GymConsumer(WebsocketConsumer):
    
    branches = {}
    users = {}
    lock = threading.Lock() 
    def connect(self):
        self.branch_id = self.scope.get('url_route').get('kwargs').get('branch_id')
        self.workout_id = self.scope.get('url_route').get('kwargs').get('workout_id') or None
        self.user = self.scope.get('user')
        self.flag = False
        with self.lock:
            if self.branch_id not in self.branches:
                self.branches[self.branch_id] = {
                    'excercises':{},
                    'events':{},
                }

            if self.user.pk not in self.users:
                self.users[self.user.pk] = {
                    'excercises':[],
                }
                
            else:
                self.flag = True
                return self.close(code=400)
            
        if self.workout_id is not None:
            Gym_Session_Mixin.get_tracked_equipment(self.workout_id, self.user, self.users, self.branch_id, self.branches )
            
            
        try:
            self.client = Client.objects.get(user=self.user)
        except Client.DoesNotExist:
            return self.close(code=400)

        user_channel = Gym_Session_Mixin.get_user_channel(self.user, self.channel_name)
        self.group_name = f'gym_session{self.branch_id}'
        
        async_to_sync(self.channel_layer.group_add) (
            self.group_name,
            user_channel.channel_name
        )
        print(self.channel_layer.groups)
        print(self.users)
        
        self.accept()
        
        print(self.branches)
        data = {
            'type':'receiver_fun',
            'events':self.branches[self.branch_id]['events']
        }
        async_to_sync(self.channel_layer.send)(self.channel_name, data)
    
    
    def disconnect(self, code):
        if self.flag :
            return super().disconnect(code)
        
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, 
            self.channel_name)
        
        self.users.pop(self.scope.get('user').pk)
        print(self.channel_layer.groups)
        
        for event in self.branches[self.branch_id]['events'].values():
            if self.scope.get('user').username in event:
                event.remove(self.scope.get('user').username)
                
        return super().disconnect(code)
    
    
    def receive(self, text_data=None, bytes_data=None):
        try:
            text_data = json.loads(text_data)
        except json.JSONDecodeError as e:
            print(str(e))
            
        data = { 
                'type':'receiver_fun',
                }
        
        branch = self.branches[self.branch_id]
        message_type = text_data.pop('type')
        
        
        if message_type == 'equipment_in_use':
            self.handle_use_equipment(text_data,branch,data)
        elif message_type == 'finish_exercise':
            self.handle_finish_exercise(text_data,branch,data)
        elif message_type =='track':
            self.handle_track(text_data,branch,data)
            
            
    def handle_use_equipment(self,text_data,branch,data):
        with self.lock:
            check = Gym_Session_Mixin.get_check(text_data['equipment_type'])

            if text_data['equipment'] in branch['events']:
                if check is not None:
                    
                    if len(branch['events'][text_data['equipment']]) >= check:
                        data['event'] = {'error':'you cannot use this equipment'}
                        async_to_sync(self.channel_layer.send)(self.channel_name,data)
                        
                    else:
                        if self.scope.get('user').username not in branch['events'][text_data['equipment']]:
                            data = Gym_Session_Mixin.use_equipment(self.branches, self.branch_id, text_data, self.scope.get('user').username, data, check)
                        async_to_sync(self.channel_layer.group_send)(self.group_name,data)
            else:
                
                if check is not None:
                    branch['events'][text_data['equipment']] = []
                    data = Gym_Session_Mixin.use_equipment(self.branches, self.branch_id, text_data, self.scope.get('user').username, data, check)
                    async_to_sync(self.channel_layer.group_send)(self.group_name,data)
            
        
    def handle_finish_exercise(self,text_data,branch,data):
    
        finishing_flag = True
        try:
            branch['events'][str(text_data['equipment'])].remove(self.scope.get('user').username)
        except Exception as e:
            finishing_flag = False
            data['error'] = 'you did not started the exercise yet'
            async_to_sync(self.channel_layer.group_send)(self.group_name,data)
            
        if finishing_flag:
            data['event'] = {
                            'action': 'finish exercise',
                            'equipment': text_data['equipment'],
                            'available': 'available',
                            'current_users':self.branches[self.branch_id]['events'][str(text_data['equipment'])]
                            }
            async_to_sync(self.channel_layer.group_send)(self.group_name,data)
    
    
    
    def handle_track(self,text_data,branch,data):
        
        if self.workout_id is not None:
            if self.user.pk in self.users:
                
                check_track = text_data['next'] + text_data['previous']
                
                if check_track != 1 :
                    pass
                
                else:
                    order = self.users[self.user.pk]['current_order']
                    exercises = self.users[self.user.pk]['excercises']
                    if (order == len(exercises)-1) and (text_data['next']):
                        data['error'] = 'your training session is done head to the cardio section or you are done for today'
                        exercise = exercises[order]
                        data['final_equipment_in_current_session']  = branch['excercises'][exercise]
                        async_to_sync(self.channel_layer.send)(self.channel_name, data)
                        
                    else:   
                        if text_data ['next'] :
                            order += 1
                            
                        elif text_data ['previous'] :
                            if order > 0 :
                                order -= 1
                                
                        order = 0 if self.users[self.user.pk]['current_order'] < 0 else order
                        self.users[self.user.pk]['current_order'] = order  
                        
                        exercise = exercises[order]
                        tracked_equipments =branch['excercises'][exercise]
                        data['tracked_equipments'] = tracked_equipments    
                        data['exercise'] = exercise
                        if order == len(exercises) - 1:
                            data['note'] = 'This is the Last Exercise For Today head to the cardio section or you are done for today'
                            
                        async_to_sync(self.channel_layer.send)(self.channel_name, data)
                        
        else:
            data['error'] = 'you do not have a workout plan to be tracked'
            async_to_sync(self.channel_layer.send)(self.channel_name, data)
                
                
    def receiver_fun(self,data):
        data.pop('type')
        self.send(json.dumps(data))
        
        
gym_consumer = GymConsumer.as_asgi()