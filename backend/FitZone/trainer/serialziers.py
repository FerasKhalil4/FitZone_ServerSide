from rest_framework import serializers
from .models import *
from user.serializers import ClientSerializer


class Client_TrainerSerializer(serializers.ModelSerializer):
    Trainer_registration_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    client_details =serializers.SerializerMethodField()
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.filter(user__is_deleted=False),write_only=True)

    class Meta:
        model = Client_Trainer
        fields =['Trainer_registration_id','client','client_details','trainer','start_date','end_date','start_hour','end_hour','registration_type','registration_status','rejection_reason']
        
    def validate_registration_status(self,data):
        if data not in['pending','accepted','rejected']:
            raise serializers.ValidationError('Invalid registration status, choose: pending, accepted, rejected')
        return data
    
    def validate_registration_type(self,data):
        if data not in ['private','online']:
            raise serializers.ValidationError('Invalid registration type, choose: private, online')
        return data
    
    def get_client_details(self,obj):
        try:
            client = Client.objects.get(id=obj.client.pk)
            serializer = ClientSerializer(client).data
            gender = 'male' if serializer['user']['gender'] == True else 'female'
            data = {
                'age':serializer['user']['age'],
                'gender':gender,
                'height':serializer['height'],
                'history':serializer['history'],
                'BMI':serializer['current_BMI'],
                'image_path':serializer['image_path'],
                'current_weight':serializer['current_weight']
            }
            return data
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
