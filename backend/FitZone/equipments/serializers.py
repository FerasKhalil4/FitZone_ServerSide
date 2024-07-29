from rest_framework import serializers
from .models import *
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse        


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id','name','description','muscle_group']

class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = '__all__'
        
class LimitationsSerializer(serializers.ModelSerializer):
    diseases= DiseaseSerializer(source ='disease',read_only=True)
    limitation_id = serializers.PrimaryKeyRelatedField(source = 'id',read_only=True)
    class Meta:
        model = Limitations
        fields = ['limitation_id','disease','equipment','diseases']
        
        
class Equipment_ExerciseSerializer(serializers.ModelSerializer):
    video_path = serializers.FileField(required=False)
    exercise_details = ExerciseSerializer(source = "exercise",read_only=True )
    exercise = serializers.PrimaryKeyRelatedField(queryset = Exercise.objects.all(),write_only=True)
    class Meta:
        model = Equipment_Exercise
        fields = ['id','equipment','exercise','video_path','exercise_details']
        
class EquipmentSerializer(serializers.ModelSerializer):
    exercise = Equipment_ExerciseSerializer(read_only=True,many = True)
    limitations = LimitationsSerializer(source='diseases',read_only=True,many = True)
    class Meta:
        model = Equipment
        fields = ['id','name', 'description', 'url', 'qr_code_image','exercise','limitations']
    
    def create(self,validated_data):
        request = self.context.get('request')
        base_url = get_current_site(request)
        equipment = Equipment.objects.create(**validated_data)
        url = f"http://{base_url}{reverse('equipment_detail', args=[str(equipment.pk)])}"
        equipment.url = url
        equipment.save()
        return equipment
    
 
class Diagrams_EquipmentsSerializer(serializers.ModelSerializer):
    equipment_details = EquipmentSerializer(source ='equipment',read_only = True)
    equipment = serializers.PrimaryKeyRelatedField(queryset=Equipment.objects.all(), write_only=True)
    diagram = serializers.PrimaryKeyRelatedField(queryset=Diagram.objects.all(),write_only=True)
    Equipment_Diagram_id = serializers.PrimaryKeyRelatedField(source = 'id',read_only=True)
    class Meta:
        model = Diagrams_Equipments
        fields= ['Equipment_Diagram_id','equipment','diagram','status','x_axis','y_axis','equipment_details']
        
        
    def validate(self,data):
        instance = self.context.get('instance',None)
        diagram = self.context.get('diagram')
        if instance is None:
            diagram_equipment = Diagrams_Equipments.objects.filter(diagram=diagram , x_axis = data.get('x_axis')
                                                                   , y_axis = data.get('y_axis'),is_deleted = False)
            print(diagram_equipment)
            if diagram_equipment.exists():
                raise serializers.ValidationError('This position is already taken')
            
        else:
            diagram_equipment = Diagrams_Equipments.objects.filter(diagram=diagram , x_axis = data.get('x_axis')
                                                                   , y_axis = data.get('y_axis'),is_deleted = False).exclude(pk=instance.pk)
            if diagram_equipment.exists():
                raise serializers.ValidationError('This position is already taken')
            
        return data
        

class DiagramSerialzier(serializers.ModelSerializer):
    equipment =  Diagrams_EquipmentsSerializer(read_only=True, many=True)
    
    class Meta:
        model = Diagram
        fields = ['id','floor','branch', 'equipment','height','width']
    
    
    def get_equipment(self,obj):
        try:
            
            equipments = Diagrams_Equipments.objects.filter(diagram=obj, is_deleted=False)
            return Diagrams_EquipmentsSerializer(equipments,many=True).data
        except Exception as e:
            raise serializers.ValidationError(str(e))