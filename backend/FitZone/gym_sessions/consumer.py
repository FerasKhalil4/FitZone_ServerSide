from channels.generic.websocket import WebsocketConsumer
from .models import Branch_Sessions
from chat.models import UserChannel
from user.models import Client
from disease.models import Client_Disease
from plans.models import Workout_Exercises
from gym.models import Branch
from equipments.models import Diagrams_Equipments,Equipment_Exercise
from equipments.serializers import Diagrams_EquipmentsSerializer, Equipment_ExerciseSerializer
from asgiref.sync import async_to_sync
from datetime import datetime,timezone, timedelta
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
    def get_diseases(equipment_id):
        
        limitations_ = {}
        exercises = Equipment_Exercise.objects.filter(equipment = equipment_id,trainer=None)
        for exercise in exercises:
            limitations = exercise.disease.values()
            if len(limitations) > 0 :
                limitations_[f'{exercise.pk}'] = [limitation['disease_id'] for limitation in limitations ]
        return limitations_
    
    @staticmethod    
    def disease_check(events,equipment_id,user):
        exercises_ids = []
        print(user['diseases'] )
        print('----------------------------------------------------------------------------------')
        for exercise in events[equipment_id]['limitations']:
            check_diseases = any(disease in user['diseases'] for disease in events[equipment_id]['limitations'][exercise])
            if check_diseases :
                exercises_ids.append(exercise)
        exercise_= Equipment_Exercise.objects.filter(pk__in=exercises_ids)
        return exercise_
    
    @staticmethod
    def use_equipment(branches, branch_id, text_data, username, data, check,user):
        equipment_id = text_data['equipment']
        events = branches[branch_id]['events']
        print(user)
        if 'users' not in events[equipment_id]:
            
            events[equipment_id] = {
                    'users':[],
                    'limitations':{}
                }
            
            limitations_ = Gym_Session_Mixin.get_diseases(equipment_id)
            events[equipment_id]['limitations'] = limitations_
        print( branches[branch_id]['events'])
            
        print('hereee')
        print(events)
        print(events[equipment_id]['limitations'])
        exercise_ = Gym_Session_Mixin.disease_check(events,equipment_id,user)
        print(exercise_)
        print('000000000000000000000000000000')
        data['limited_exercises']  = [{
                                    'equipmeny_exercise_id':exercise.pk,
                                    'exercise_name':exercise.exercise.name ,
                                       'equipment_name':exercise.equipment.name,
                                       'video_path':str(exercise.video_path),
                                       } for exercise in exercise_] if len(exercise_) != 0 else None
        print(data['limited_exercises'])
        
        events[equipment_id]['users'].append(username)
        data['event'] = {
                        'equipment':equipment_id,
                        'action':'start exercise',
                        'current_users':events[equipment_id]['users']
                         }
        
        if len(events[equipment_id]['users']) == check:
            data['event']['status'] = 'unavilable'
        
        return data


    @staticmethod
    def get_tracked_equipment(workout_id, user, users, branch_id, branches):
        
        branch = branches[branch_id]
        exercises = Workout_Exercises.objects.filter(workout=workout_id).order_by('order')
        
        for exercise in exercises:
            
            branch_equipment = Diagrams_Equipments.objects.filter(diagram__branch = branch_id
                                                                , equipment = exercise.exercise.equipment.pk,status=True,is_deleted=False)
            
            equipments_data = Diagrams_EquipmentsSerializer(branch_equipment,many=True).data
            branch_equipment = branch_equipment.values_list('pk', flat=True)
            exercise_data = Equipment_ExerciseSerializer(exercise.exercise).data
            
            users[user.pk]['current_order'] = -1
            users[user.pk]['excercises'].append(exercise_data)
            
            if exercise.exercise.pk not in branch['excercises']['excercises_data']:
                branch['excercises']['excercises_data'][exercise.exercise.pk] = []
                for equipment in equipments_data:
                    branch['excercises']['excercises_data'][exercise.exercise.pk].append(equipment)
            else:
                for equipment in equipments_data:
                    if equipment not in branch['excercises']['excercises_data'][exercise.exercise.pk]:
                        branch['excercises']['excercises_data'][exercise.exercise].append(equipment)
        
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
        print(self.user.pk)
        

        try:
            with self.lock:
                print('locking')
                if self.branch_id not in self.branches:
                    print('branch does not exist')
                    self.branches[self.branch_id] = {
                        'excercises':{
                            'equipments':[],
                            'excercises_data':{}
                            },
                        'events':{},
                    }

                if self.user.pk not in self.users:
                    print('user not exists')
                    self.users[self.user.pk] = {
                        'excercises':[],
                        'diseases':[]
                    }
                    
                else:
                    print('user error')
                    self.flag = True
                    return self.close(code=400)
        except Exception as e:
            print(str(e))
            return self.close(code=400)
            
            
                
        if self.workout_id is not None:
            Gym_Session_Mixin.get_tracked_equipment(self.workout_id, self.user, self.users, self.branch_id, self.branches )
            
            
        try:
            print('get_client')
            self.client = Client.objects.get(user=self.user)
        except Client.DoesNotExist:
            return self.close(code=400)
        
        print('branch')
        branch=Branch.objects.get(pk=self.branch_id)
        print('create branch session')
        self.session = Branch_Sessions.objects.create(
                    client = self.client,
                    branch = branch,
                )
        
        client_diseases = Client_Disease.objects.filter(client=self.client).values_list('disease_id', flat=True)
        for disease in client_diseases:
            self.users[self.user.pk]['diseases'].append(disease)
        user_channel = Gym_Session_Mixin.get_user_channel(self.user, self.channel_name)
        self.group_name = f'gym_session{self.branch_id}'
        
        async_to_sync(self.channel_layer.group_add) (
            self.group_name,
            user_channel.channel_name
        )

        self.accept()
        sent_data = {id:{"users":item['users']} for id, item in self.branches[self.branch_id]['events'].items()}
        print(sent_data)
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
        print(self.branches[self.branch_id]['events'])
        for event in self.branches[self.branch_id]['events'].values():
            if self.scope.get('user').username in event['users']:
                event['users'].remove(self.scope.get('user').username)
            print( self.branches[self.branch_id]['events'])
        
        self.session.end_session = datetime.now(timezone(timedelta(hours=3)))
        self.session.save()

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
        try:
            with self.lock:
                check = Gym_Session_Mixin.get_check(text_data['equipment_type'])

                if text_data['equipment'] in branch['events']:
            
                    if check is not None:
                        
                        if len(branch['events'][text_data['equipment']]['users']) >= check:
                            data['event'] = {'error':'you cannot use this equipment'}
                            async_to_sync(self.channel_layer.send)(self.channel_name,data)
                            
                        else:
                            if self.scope.get('user').username not in branch['events'][text_data['equipment']]:
                                data = Gym_Session_Mixin.use_equipment(self.branches, self.branch_id, text_data, self.scope.get('user').username, data, check,self.users[self.user.pk])
                                if 'error' in data : 
                                    async_to_sync(self.channel_layer.send)(self.channel_name,data)
                                else:
                                    async_to_sync(self.channel_layer.send)(self.channel_name,data)
                                    print(data['limited_exercises'])
                                    print('-----------------------------')
                                    data.pop('limited_exercises')
                                    for channel in self.channel_layer.groups.get(self.group_name):
                                        if channel != self.channel_name:
                                            async_to_sync(self.channel_layer.send)(channel,data)

                else:
                    
                    if check is not None:
                        branch['events'][text_data['equipment']] = {}
                        data = Gym_Session_Mixin.use_equipment(self.branches, self.branch_id, text_data, self.scope.get('user').username, data, check,self.users[self.user.pk])
                        if 'error' in data: 
                            async_to_sync(self.channel_layer.send)(self.channel_name,data)
                        else:
                            async_to_sync(self.channel_layer.send)(self.channel_name,data)
                            print(data['limited_exercises'])
                            print('-----------------------------')
                            data.pop('limited_exercises')
                            for channel in self.channel_layer.groups.get(self.group_name):
                                if channel != self.channel_name:
                                    async_to_sync(self.channel_layer.send)(channel,data)
        
            print(self.branches[self.branch_id]['events'])
        except Exception as e:
            print(str(e))
            return self.close(code=400)
            
        
    def handle_finish_exercise(self,text_data,branch,data):
    
        finishing_flag = True
        try:
            branch['events'][text_data['equipment']]['users'].remove(self.scope.get('user').username)
        except Exception as e:
            finishing_flag = False
            data['error'] = 'you did not started the exercise yet'
            async_to_sync(self.channel_layer.group_send)(self.group_name,data)
            
        if finishing_flag:
            data['event'] = {
                            'action': 'finish exercise',
                            'equipment': text_data['equipment'],
                            'available': 'available',
                            'current_users':self.branches[self.branch_id]['events'][text_data['equipment']]
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
                    print(exercises)
                    if (order == len(exercises)-1) and (text_data['next']):
                        data['error'] = 'your training session is done head to the cardio section or you are done for today'
                        exercise = exercises[order]
                        data['final_equipment_in_current_session']  = branch['excercises']['excercises_data'][exercise['equipment_exercise_id']]
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
 
                        tracked_equipments =branch['excercises']['excercises_data'][exercise['equipment_exercise_id']]
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