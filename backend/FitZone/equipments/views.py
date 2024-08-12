from rest_framework import generics, status 
from rest_framework.response import Response
from .serializers import *
from community.paginations import Pagination
from django.db import transaction
from django.db.models import Q
import json

class ExercisesMixin():
    def exercises_list(self, equipments, trainer=None):
        try:
            exercises = []
            trainer = trainer.pk if trainer is not None else None
            query = Q(
                trainer=trainer
            )
            print(equipments)
            for instance in equipments:
                query |= Q(equipment = instance.equipment)
                exercises_ = Equipment_Exercise.objects.filter(query).distinct('equipment','exercise','trainer')
                serializer = Equipment_ExerciseSerializer(exercises_,many=True)
                for item in serializer.data:
                    if item not in exercises_:
                        exercises.append(item)
            return exercises
        except Exception as e:
            raise serializers.ValidationError(str(e))
        

    
class ExerciseListAV(generics.ListAPIView):
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.all()
    
excerciseList = ExerciseListAV.as_view()

class EquipmentExerciseListAV(ExercisesMixin,generics.ListCreateAPIView):
    serializer_class = Equipment_ExerciseSerializer
    queryset = Equipment_Exercise.objects.all()
    def get(self, request, *args, **kwargs):
        equipments = Diagrams_Equipments.objects.filter(diagram__branch = self.kwargs.get('branch_id') 
                                                        , status =True).distinct('equipment')   
        user = request.user
        trainer = None
        if request.user.role == 4:
            trainer = Trainer.objects.get(employee__user = user)
            exercises = self.exercises_list(equipments, trainer)
        else:
            exercises = self.exercises_list(equipments)
        return Response({'data':exercises},status=status.HTTP_200_OK)  
            
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                user = request.user
                equipments = request.data.pop('equipments')
                if 'exercise_id' in request.data:
                    exercise = Exercise.objects.get(id=request.data['exercise_id'])
                elif 'exercise_id' not in request.data:
                    exercise_serialzier = ExerciseSerializer(data=request.data)
                    exercise_serialzier.is_valid(raise_exception=True)
                    exercise = exercise_serialzier.save()
                else :
                    return Response({'error':'please provide a valid exercise data or exercise id'}, status=status.HTTP_400_BAD_REQUEST)
                trainer = Trainer.objects.get(employee__user = user)
                
                for equipment in equipments:
                    equipment['exercise'] = exercise.pk
                    equipment['trainer'] = trainer.pk
                    serializer = self.get_serializer(data=equipment)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                return Response({'success':'exercise created successfully'},status=status.HTTP_201_CREATED)                    
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)   
                
            
        
equipment_excerciseList = EquipmentExerciseListAV.as_view()

def check_validatiy(item):
    if isinstance(item,str):
        try:
            item=json.loads(item)
        except json.JSONDecodeError:
            raise ValueError('invalid format')
        return item

class EquipmentsListAV(generics.ListCreateAPIView):
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()
    pagination_class = Pagination   
    
    def post(self, request, *args, **kwargs):
        data = request.data.dict()

        data['equipment'] = check_validatiy(data.pop('equipment',None))
        data['exercises'] = check_validatiy(data.pop('exercises',None))
        data['diseases'] = check_validatiy(data.pop('diseases',[]))
        try:
            with transaction.atomic():
                data['equipment']['image_path'] = data.pop('image_path',None)
                serializer = EquipmentSerializer(data=data['equipment'],context = {'request': request})
                serializer.is_valid(raise_exception=True)
                equipment = serializer.save()
                relation_data = {'equipment_id':equipment.pk}
            
                video_path = data.pop('video_path', None)
                if 'exercise_id' not in data:
                    exercise_serializer = ExerciseSerializer(data= data['exercises'])
                    exercise_serializer.is_valid(raise_exception=True)
                    exercise = exercise_serializer.save()
                    
                    relation_data['exercise_id'] =exercise.pk
                    relation_data['video_path'] = video_path
                    
                else:
                    relation_data['exercise_id'] =data.pop('exercise_id', None)
                    relation_data['video_path'] = video_path 
                Equipment_Exercise.objects.create(**relation_data)
                
                for disease in data['diseases']:

                    limitation_data = {'disease':disease['id'], 'equipment':equipment.pk}
                    limitation_serializer = LimitationsSerializer(data=limitation_data)
                    if limitation_serializer.is_valid(raise_exception=True):
                        limitation_serializer.save()
                        print(limitation_serializer.data)
                return Response({'message':'equipment created Succcefully'}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            raise serializers.ValidationError(str(e))
            
Equipment_lisAtV = EquipmentsListAV.as_view()

class EquipmentsDetailAV(generics.RetrieveAPIView):
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()
    
Equipment_detailAV = EquipmentsDetailAV.as_view()


    
class DiagramListAV(generics.ListCreateAPIView):
    serializer_class = DiagramSerialzier
    queryset = Diagram.objects.all()
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        try:
            qs = Diagram.objects.filter(branch= kwargs.get('branch_id'))
            page = self.pagination_class()
            page_qs = page.paginate_queryset(qs,request)
            serialzier = self.get_serializer(page_qs, many = True)
            return page.get_paginated_response(serialzier.data)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                branch_id = kwargs.get('branch_id')
                data['branch'] = branch_id
                diagram = Diagram.objects.filter(branch=branch_id, floor = data.get('floor'))
                if diagram.exists():
                    return Response({'error':'Existing diagram'},status=status.HTTP_400_BAD_REQUEST)
                
                diagram_serializer = DiagramSerialzier(data=data, context = {'request': request})
                if diagram_serializer.is_valid(raise_exception=True):
                    diagram_serializer.save()
                return Response(diagram_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise serializers.ValidationError(str(e))
            
diagram_listAV = DiagramListAV.as_view()

class DiagramDetailAV(generics.RetrieveUpdateAPIView):
    serializer_class = DiagramSerialzier
    queryset = Diagram.objects.all()
    def put(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                existed_equipments = data['existed_equipments']
                added_equipments = data['added_equipments']
                equipments_diagram = Diagrams_Equipments.objects.filter(diagram = self.kwargs['diagram_id'])
                ids = [item.id for item in equipments_diagram]
                
                diagram = Diagram.objects.get(id=self.kwargs['diagram_id'])
                
                for id , equipment_data in existed_equipments.items():
                    ids.remove(int(id))
                    instance = Diagrams_Equipments.objects.get(id=id)
                    serializer = Diagrams_EquipmentsSerializer(instance,data=equipment_data,partial=True,
                                                               context = {'diagram':diagram,'instance':instance})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                for id , equipment_data in added_equipments.items():
                    for details in equipment_data:
                        details['equipment'] = id 
                        details['diagram'] = self.kwargs['diagram_id']
                        serializer = Diagrams_EquipmentsSerializer(data=details,partial=True,context = {'diagram':diagram})
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                for id in ids:
                    remove_data = Diagrams_Equipments.objects.get(pk = id)
                    remove_data.is_deleted = True
                    remove_data.save()
                    
                
                return Response(serializer.data, status = status.HTTP_200_OK)  
        except Exception as e:
            raise serializers.ValidationError(str(e))

        
diagram_detailsAV = DiagramDetailAV.as_view()
    
class DiagramEquipmentsAV(generics.ListCreateAPIView):
    serializer_class = Diagrams_EquipmentsSerializer
    queryset = Diagrams_Equipments.objects.all()
    
    def get(self, request, *args, **kwargs):
        qs = Diagram.objects.filter(pk=self.kwargs['diagram_id'])
        return Response(DiagramSerialzier(qs,many=True).data,status=status.HTTP_200_OK)
        
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                equipments = request.data['equipment']
                diagram = Diagram.objects.get(pk=self.kwargs['diagram_id'])
                for id , positions in equipments.items():
                    for position in positions:
                        position['equipment'] = id
                        position['diagram'] = self.kwargs['diagram_id']
                        DE_serializer = Diagrams_EquipmentsSerializer(data=position, context = {'diagram':diagram})
                        if DE_serializer.is_valid(raise_exception=True):
                            DE_serializer.save()
                return Response({'success':'equipments added successfully'},status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

diagramEquipmentsCreate = DiagramEquipmentsAV.as_view()



