from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import *
from gym.permissions import admin_permissions 

class PointsListAV(generics.ListAPIView):
    serializer_class = PointsSerializer
    queryset = Points.objects.all()
    permission_classes = [admin_permissions]

pointList = PointsListAV.as_view()

class PointsDetailsAV(generics.RetrieveUpdateAPIView):
    serializer_class = PointsSerializer
    queryset = Points.objects.all()
    permission_classes = [admin_permissions]
    
    def put(self, request, pk, *args, **kwargs):
        data = request.data 
        try:
            point = self.get_object()
            serializer = self.get_serializer(point, data = data, partial = True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message":"point instance updated Successfully","data":serializer.data}, status=status.HTTP_200_OK)
        except Points.DoesnotExist:
            return Response({"message":"point instance not found"}, status= status.HTTP_404_NOT_FOUND)
        except Exception as e:
            raise serializers.ValidationError(str(e))
pointsDetails = PointsDetailsAV.as_view()