from rest_framework import serializers
from .models import *
from user.serializers import ClientSerializer
from gym.seriailizers import GymSerializer

days_of_week = {
    1: 'sunday',
    2: 'monday',
    3: 'tuesday',
    4: 'wednesday',
    5: 'thursday',
    6: 'friday',
    7: 'saturday'
}

now = datetime.datetime.now()

class TrainerGroupsSerializer(serializers.ModelSerializer):
    gym_data = GymSerializer(source='gym',read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(source = 'id', read_only=True)
    current_group_capacity = serializers.SerializerMethodField()
    class Meta:
        model = TrainerGroups
        fields = ['group_id','clients','trainer','gym','start_hour','end_hour','group_capacity','days_off','gym_data','current_group_capacity']
        
    def get_current_group_capacity(self,obj):
        capacity = Client_Trainer.objects.filter(group = obj.pk,start_date__lte = now,end_date__gte=now).count()
        return capacity
        
    def get_days(self, days):
        return{day:name for day, name in days_of_week.items() if name in days.values()}
    
    def validate_days_on(self,data):
        return self.get_days(data)
    
    def create(self, validated_data):
        return super().create(validated_data)
    
        
class Client_TrainerSerializer(serializers.ModelSerializer):
    Trainer_registration_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    client_details =serializers.SerializerMethodField()
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.filter(user__is_deleted=False),write_only=True)
    group_data = TrainerGroupsSerializer(source="group",read_only=True)

    class Meta:
        model = Client_Trainer
        fields =['Trainer_registration_id','group_data','client','client_details','trainer','start_date','end_date','registration_type','registration_status','rejection_reason','group']
        
    
    def get_client_details(self,obj):
        try:
            client = Client.objects.get(id=obj.client.pk)
            serializer = ClientSerializer(client).data
            gender = 'male' if serializer['user']['gender'] == True else 'female'
            serializer['history'][0].pop('number_updates', None)
            data = {
                'age':serializer['user']['age'],
                'gender':gender,
                'height':serializer['height'],
                'current_goal':serializer['history'],
                'BMI':serializer['current_BMI'],
                'image_path':serializer['image_path'],
                'current_weight':serializer['current_weight']
            }
            return data
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
