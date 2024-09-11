from rest_framework import generics, status
from rest_framework.response import Response
from .models import *
from .serializers import FeedbackSerializer,RateSerializer,CreateRateSerializer,GymRateSerializer,TrainerRateSerializer
from drf_spectacular.utils import extend_schema
from .services import RateService
from .DataExamples import * 


class RateListAV(generics.ListAPIView):
    
    serializer_class = RateSerializer
    queryset = Rate.objects.all()
    
    @extend_schema(
    summary='return all the rates in the app based on the request user'
)
    def get(self, request, *args, **kwargs):
        qs = RateService.get_ratings(request.user)

        if ((qs['gym_ratings'] is not None) and (qs['trainer_ratings'] is not None)) :
            gym_ratings = GymRateSerializer(qs['gym_ratings'],many=True).data
            trainer_ratings = TrainerRateSerializer(qs['trainer_ratings'],many=True).data
            return Response({
                'gym_ratings':gym_ratings,
                'trainer_ratings':trainer_ratings,
            },status=status.HTTP_200_OK)
            
        elif qs['trainer_ratings'] is not None :
            trainer_ratings = TrainerRateSerializer(qs['trainer_ratings'],many=True).data
            return Response({
                'trainer_ratings':trainer_ratings,
            },status=status.HTTP_200_OK)
            
        elif qs['ratings'] is not None:
            ratings = RateSerializer(qs['ratings'],many=True).data
            return Response({
                'ratings':ratings,
            },status=status.HTTP_200_OK)
            
            
rate_list = RateListAV.as_view()
    

class RateCreateAV(generics.CreateAPIView):
    
    serializer_class = CreateRateSerializer
    queryset = Rate.objects.all()
    
    @extend_schema(
    summary='rate either branch, trainer, or app',
    examples = rate_create
)
    
    def post(self, request,*args, **kwargs):
        try:
            request.data['client'] =  Client.objects.get(user = request.user.pk).pk
            return super().post(request,*args,**kwargs)
            
        except Client.DoesNotExist:
            return Response({'error': 'client does not exist'},status=status.HTTP_404_NOT_FOUND)
rate_create = RateCreateAV.as_view()

class GymRateDetailsAV(generics.RetrieveUpdateAPIView):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()
    
    def get_object(self):
        return Rate.objects.get(gym_rate__gym =self.kwargs['branch_id'],client=Client.objects.get(user=self.request.user.pk),is_deleted=False)
    
    
    @extend_schema(
    summary='get the specific rate related to client for specifc branch'
)
    def get(self,request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)            
        except Rate.DoesNotExist:
            return Response({'error': 'rate does not exist'},status=status.HTTP_404_NOT_FOUND)
        
    @extend_schema(
    summary='update the client rate for specifc branch'
)
        
    def put(self,request, *args, **kwargs):
        try:
            request.data['client'] = Client.objects.get(user=request.user.pk).pk
            serializer = self.get_serializer(self.get_object(),request.data,context = {'branch_id':kwargs['branch_id']})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'message':'rate updated successfully'}, status=status.HTTP_200_OK)
        except Client.DoesNotExist or Exception :
            return Response({'error': 'client does not exist'},status=status.HTTP_404_NOT_FOUND)        
        
gym_rate_details = GymRateDetailsAV.as_view()
        
        
        
        
class TrainerRateDetailsAV(generics.RetrieveUpdateAPIView):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()
    
    def get_object(self):
        return Rate.objects.get(trainer_rate__trainer =self.kwargs['trainer_id'],client=Client.objects.get(user=self.request.user.pk),is_deleted=False)
    
    @extend_schema(
    summary='get the specific rate related to client for specifc trainer'
)
    def get(self,request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)            
        except Rate.DoesNotExist:
            return Response({'error': 'rate does not exist'},status=status.HTTP_404_NOT_FOUND)
        
    @extend_schema(
    summary='update the client rate for specifc trainer'
)
        
    def put(self,request, *args, **kwargs):
        try:
            request.data['client'] = Client.objects.get(user=request.user.pk).pk
            serializer = self.get_serializer(self.get_object(),request.data,context = {'trainer_id':kwargs['trainer_id']})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'message':'rate updated successfully'}, status=status.HTTP_200_OK)
        except Client.DoesNotExist or Exception :
            return Response({'error': 'client does not exist'},status=status.HTTP_404_NOT_FOUND)        
        
trainer_rate_details = TrainerRateDetailsAV.as_view()
        
        
        
class AppRateDetailsAV(generics.RetrieveUpdateAPIView):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()
    
    def get_object(self):
        return Rate.objects.get(pk=self.kwargs['pk'],is_app_rate = True, client=Client.objects.get(user=self.request.user.pk),is_deleted=False)
    
    
    @extend_schema(
    summary='get the specific rate related to client for the app'
)
    def get(self,request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)            
        except Rate.DoesNotExist:
            return Response({'error': 'rate does not exist'},status=status.HTTP_404_NOT_FOUND)
        
        
    @extend_schema(
    summary='update the client rate for the app'
)
        
    def put(self,request, *args, **kwargs):
        try:
            request.data['client'] = Client.objects.get(user=request.user.pk).pk
            serializer = self.get_serializer(self.get_object(),request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'message':'rate updated successfully'}, status=status.HTTP_200_OK)
        except Client.DoesNotExist or Exception :
            return Response({'error': 'client does not exist'},status=status.HTTP_404_NOT_FOUND)        
        
app_rate_details = AppRateDetailsAV.as_view()
        
        
class FeedbackListAV(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        request.data['client'] = Client.objects.get(user=request.user.pk).pk
        return super().post(request, *args, **kwargs)
    
feedback_list = FeedbackListAV.as_view()

class FeedbackDetailsAV(generics.RetrieveUpdateAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    
    def get(self, request, *args,**kwargs):
        return super().get(request, *args,**kwargs)
    
    def put(self,request,*args, **kwargs):
        
        serialzier = self.get_serializer(self.get_object(),request.data,partial=True)
        if serialzier.is_valid(raise_exception=True):
            serialzier.save()
        return Response({'message':'feedback updated successfully'},status=status.HTTP_200_OK)
        
    
feedback_details = FeedbackDetailsAV.as_view()

    