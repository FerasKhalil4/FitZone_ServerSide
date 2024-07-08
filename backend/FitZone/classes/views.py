from rest_framework import generics, status ,serializers
from rest_framework.response import Response
from .models import *
from .serializers import *

class ClassesListAV(generics.ListCreateAPIView):
    serializer_class = ClassesSerializer
    queryset = Classes.objects.all()
    
    def post(self, request, *args, **kwargs):
        serializer = ClassesSerializer(data=request.data ,context = {'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

classesListAV = ClassesListAV.as_view()
    
class ClassesDetailAV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassesSerializer
    queryset = Classes.objects.filter(is_deleted = False)
    
    
    def update(self,request, pk, *args , **kwargs):
        class_data = Classes.objects.get(pk = pk)
        serializer = self.get_serializer(class_data, data = request.data ,context = {'request': request, 'instance':class_data})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)
        
    def destroy(self,request, pk, *args , **kwargs):
        class_data = Classes.objects.get(pk = pk)
        class_data.is_deleted = True
        class_data.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
classesDetailAV = ClassesDetailAV.as_view()
