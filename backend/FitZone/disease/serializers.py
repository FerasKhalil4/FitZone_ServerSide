from rest_framework import serializers
from .models import *
class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = '__all__'
        
class LimitationsSerializer(serializers.ModelSerializer):
    diseases= DiseaseSerializer(source ='disease',read_only=True)
    limitation_id = serializers.PrimaryKeyRelatedField(source ='id',read_only=True)
    
    class Meta:
        model = Limitations
        fields = ['limitation_id','disease','exercise','diseases']
        
        

class Client_DiseaseSerilaizer(serializers.ModelSerializer):
    client_disease_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    disease_name =serializers.CharField(source='disease.name',read_only=True)
    class Meta:
        model = Client_Disease
        fields = ['client_disease_id','client','disease','disease_name']
         