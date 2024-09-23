from rest_framework import serializers
from .models import *
from user.serializers import ClientSerializer
from gym.seriailizers import GymSerializer,TrainerSerialzier
from .services import SubscripeWithTrainerService,UpdateSubscriptionWithTrainerService
from gym.models import Branch


days_of_week = {
    1: 'sunday',
    2: 'monday',
    3: 'tuesday',
    4: 'wednesday',
    5: 'thursday',
    6: 'friday',
    7: 'saturday'
}

class Client_TrainerSerializer(serializers.ModelSerializer):
    Trainer_registration_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    client_details =serializers.SerializerMethodField()
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.filter(user__is_deleted=False),write_only=True)
    old_group_number = serializers.IntegerField(write_only=True,allow_null=True)

    class Meta:
        model = Client_Trainer
        fields =['Trainer_registration_id','client','client_details','trainer','start_date','end_date'
                 ,'registration_type','registration_status','rejection_reason','group','old_group_number']

              
    def get_client_details(self,obj):
        try:
            client = Client.objects.get(id=obj.client.pk)
            serializer = ClientSerializer(client).data
            gender = 'male' if serializer['user']['gender'] == True else 'female'
            serializer['history'][0].pop('number_updates', None)
            data = {
                'user_id':serializer['user']['id'],
                'username':serializer['user']['username'],
                'name':f"{serializer['user']['first_name']} {serializer['user']['last_name']}",
                'age':serializer['user']['age'],
                'gender':gender,
                'height':serializer['height'],
                'current_goal':serializer['history'],
                'body_data':serializer['current_BMI'],
                'image_path':serializer['image_path'],
                'current_weight':serializer['current_weight']
            }
            return data
        except Exception as e:
            raise serializers.ValidationError(str(e))
class TrainerGroupsSerializer(serializers.ModelSerializer):
    gym_data = GymSerializer(source='gym',read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(source = 'id', read_only=True)
    current_group_capacity = serializers.SerializerMethodField()
    clients= serializers.SerializerMethodField()
    
    class Meta:
        model = TrainerGroups
        fields = ['group_id','clients','trainer','gym','start_hour','end_hour','group_capacity','days_off','gym_data','current_group_capacity']
    
    
    def get_clients(self,obj):
        try:
            clients_data = []
            clients = obj.clients.values()

            for client in clients:
                if client['registration_status'] != 'accepted':
                    pass
                else:
                    client_ = Client.objects.get(pk=client['client_id'])
                    print(client_) 
                    clients_data.append({
                        'client_id':client_.pk,
                        'username':client_.user.username,
                        'name': f'{client_.user.first_name} {client_.user.last_name}'
                    })
                
            return clients_data
              
        except Exception as e:
            raise serializers.ValidationError(str(e))
       
        
    def get_current_group_capacity(self,obj):
        now = datetime.datetime.now()
        capacity = Client_Trainer.objects.filter(group = obj.pk,start_date__lte = now,end_date__gte=now,registration_status='accepted',is_deleted=False).count()
        return capacity
    
        
    def get_days(self, days):
        return{day:name for day, name in days_of_week.items() if name in days.values()}
    
    def validate_days_on(self,data):
        return self.get_days(data)
    
    def create(self, validated_data):
        return super().create(validated_data)
    
class TrainerProfileDataSerializer(TrainerSerialzier):
    groups = serializers.SerializerMethodField()
    trainer_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    class Meta:
        model = Trainer
        fields = [ 
                  'groups','trainer_id','employee','employee_id','allow_public_posts',
                  'online_training_price','private_training_price','rate','number_of_rates'
        ]
    def get_groups(self,obj):
        groups = TrainerGroups.objects.filter(trainer=obj.pk) 
        return TrainerGroupsSerializer(groups,many=True).data
        
        
class SubscriptionWithTrainerSerializer(Client_TrainerSerializer):
    # group_id = serializers.PrimaryKeyRelatedField(queryset = TrainerGroups.objects.all(),source='group',write_only=True)
    # branch = serializers.PrimaryKeyRelatedField(queryset = Branch.objects.filter(is_active=True),write_only=True)
    group_data = TrainerGroupsSerializer(source='group',read_only=True)
    class Meta:
        model = Client_Trainer
        fields = ['Trainer_registration_id','client','client_details','trainer','start_date'
                  ,'end_date','registration_type','registration_status','rejection_reason','group','group_data']
        # branch
        
    def validate(self,data):
        if 'registration_type' in data:
            if data['registration_type'] == 'private' and data['group'] is None :
                raise serializers.ValidationError('incompatible data for registrations')
            
            elif data['registration_type'] == 'online' and data['group'] is not None:
                raise serializers.ValidationError('incompatible data for registrations')
        if data['group'] is not None:
            check = TrainerGroups.objects.filter(trainer=data['trainer'].pk, pk= data['group'].pk,is_deleted=False)
            if not check.exists():
                raise serializers.ValidationError(f'the group {data['group'].pk} does not exist for this trainer {data['trainer'].employee.user.username}') 
            
        return data  
        
    def create(self, data):
        try:
            return SubscripeWithTrainerService.subscripe_with_trainer(data)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    def update(self,instance,data):
        try:
            return UpdateSubscriptionWithTrainerService.update_sub(data,instance)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        
class ClientGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerGroups
        fields = '__all__'
        
    def to_representation(self, instance):
        try:
            representation =  super().to_representation(instance)
            count = Client_Trainer.objects.filter(group=representation['id'],registration_status='accepted',is_deleted=False).count()
            if count >= representation['group_capacity']:
                representation['group_status'] = 'full'
            return representation
        except Exception as e:
            raise serializers.ValidationError(str(e))
         