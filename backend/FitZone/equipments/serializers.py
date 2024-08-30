from rest_framework import serializers
from .models import *
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse        
from disease.serializers import LimitationsSerializer,DiseaseSerializer
from django.db.models import Q

class ExerciseSerializer(serializers.ModelSerializer):
    exercise_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    class Meta:
        model = Exercise
        fields = ['exercise_id','name','description','muscle_group']


class Equipment_ExerciseSerializer(serializers.ModelSerializer):
    video_path = serializers.FileField(required=False)
    exercise_details = ExerciseSerializer(source = "exercise",read_only=True )
    exercise = serializers.PrimaryKeyRelatedField(queryset = Exercise.objects.all(),write_only=True)
    equipment_exercise_id = serializers.PrimaryKeyRelatedField(source='id', read_only=True)
    class Meta:
        model = Equipment_Exercise
        fields = ['equipment_exercise_id','equipment','exercise','video_path','exercise_details','trainer']
        
class EquipmentSerializer(serializers.ModelSerializer):
    exercise = serializers.SerializerMethodField()
    limitations = LimitationsSerializer(source='diseases',read_only=True,many = True)
    equipment_id = serializers.PrimaryKeyRelatedField(source = 'id', read_only = True)
    excerises = ExerciseSerializer(source = 'Equipment_Exercise.exercise',read_only=True,many = True)
    class Meta:
        model = Equipment
        fields = ['equipment_id','name', 'description', 'url', 'qr_code_image','exercise','limitations','excerises','image_path','category']
        
    def get_exercise(self,obj):
        try:
            trainer = self.context.get('trainer', None)
            query = Q(
                    equipment = obj.pk
                )
            if trainer is not None:
                query &= (Q( 
                    trainer = None
                    )
                   |Q(
                       trainer = trainer
                   ))
            else :
                query &= Q(
                     trainer = None
                    )
            
            qs = Equipment_Exercise.objects.filter(query)

            exercises = Equipment_ExerciseSerializer(qs,many=True).data
            return exercises
        except Exception as e:
            raise serializers.ValidationError(str(e))
    
    def create(self,validated_data):
        request = self.context.get('request')
        base_url = get_current_site(request)
        equipment = Equipment.objects.create(**validated_data)
        url = f"http://{base_url}{reverse('equipment_detail', args=[str(equipment.pk)])}"
        equipment.url = url
        equipment.save()
        return equipment
    
 
class Diagrams_EquipmentsSerializer(serializers.ModelSerializer):
    equipment_details = serializers.SerializerMethodField()
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
    
    def get_equipment_details(self, obj):
        
        try:
            trainer = self.context.get('trainer',None)
            equipments = Equipment.objects.get(pk=obj.equipment.pk) 
            return EquipmentSerializer(equipments).data if trainer is None else EquipmentSerializer(equipments,context={'trainer':trainer}).data
        except Exception as e:
            raise serializers.ValidationError(str(e))

class DiagramSerialzier(serializers.ModelSerializer):
    equipments =  serializers.SerializerMethodField()
    
    class Meta:
        model = Diagram
        fields = ['id','floor','branch', 'equipments','height','width']
    
    def get_equipments(self,obj):
        try:
            
            trainer = self.context.get('trainer',None)
            equipments = Diagrams_Equipments.objects.filter(diagram=obj, is_deleted=False) 
            return Diagrams_EquipmentsSerializer(equipments,many=True).data if trainer is None else Diagrams_EquipmentsSerializer(equipments,many=True,context={'trainer':trainer}).data 
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        
