from rest_framework import generics, status 
from rest_framework.response import Response
from .serializers import *
from community.paginations import Pagination
from django.db import transaction
class EquipmentsListAV(generics.ListCreateAPIView):
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()
    pagination_class = Pagination
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data 
        equipment_data = data.pop('equipment',None)
        exercise_data = data.pop('exercises',None)
        try:
            
            equipment_serializer = EquipmentSerializer(data=equipment_data,context = {'request':request})
            equipment_serializer.is_valid(raise_exception=True)
            equipment = equipment_serializer.save()
            relation_data = {'equipment_id':equipment.pk}
            
            for exercise_data in exercise_data:                 
                video_path = exercise_data.pop('video_path', None)
                exercise_serializer = ExerciseSerializer(data=exercise_data)
                exercise_serializer.is_valid(raise_exception=True)
                exercise = exercise_serializer.save()
                
                relation_data['exercise_id'] =exercise.pk
                relation_data['video_path'] = video_path
                
                Equipment_Exercise.objects.create(**relation_data)

            return Response(equipment_serializer.data, status=status.HTTP_201_CREATED)
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
            qs = Diagram.objects.filter(branch=request.data.get('branch'))
            page = self.pagination_class()
            page_qs = page.paginate_queryset(qs,request)
            serialzier = self.get_serializer(page_qs, many = True)
            return page.get_paginated_response(serialzier.data)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = {}
                data['branch'] = request.data.get('branch')
                data['floor'] = request.data.get('floor')
                
                diagram_serializer = DiagramSerialzier(data=data, context = {'request': request})
                if diagram_serializer.is_valid(raise_exception=True):
                    diagram = diagram_serializer.save()
                    
                for id , positions in request.data.get('equipment').items():
                    for position in positions:
                        position['equipment'] = id
                        position['diagram'] = diagram.pk
                        DE_serializer = Diagrams_EquipmentsSerializer(data=position, context = {'request': request})
                        if DE_serializer.is_valid(raise_exception=True):
                            DE_serializer.save()
                return Response(request.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise serializers.ValidationError(str(e))
            
diagram_listAV = DiagramListAV.as_view()

class DiagramDetailAV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = Diagrams_EquipmentsSerializer
    queryset = Diagrams_Equipments.objects.filter(is_deleted=False)
    def put(self, request, pk, *args, **kwargs):
        try:
            object_ = self.get_object()
            serializer = self.get_serializer(object_, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)  
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def delete(self, request, pk, *args, **kwargs):
        object_ = self.get_object()
        object_.is_deleted = True
        object_.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
diagram_detailsAV = DiagramDetailAV.as_view()
    