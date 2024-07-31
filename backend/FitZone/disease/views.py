from rest_framework import generics, status 
from rest_framework.response import Response
from .serializers import *
from .DataExample import *
from drf_spectacular.utils import extend_schema
from django.db import transaction


@extend_schema(
    summary='get the common pains and diseaeses'
)
class DiseasesListAV(generics.ListAPIView):
    serializer_class = DiseaseSerializer
    queryset = Disease.objects.all()
    
disease_list = DiseasesListAV.as_view()


@extend_schema(
    summary='get the common pains and diseaeses related to specific equipment'
)
class LimitationListAV(generics.ListCreateAPIView):
    serializer_class = LimitationsSerializer
    
    def get_queryset(self):
        return Limitations.objects.filter(equipment = self.kwargs.get('equipment_pk'))
 
    @extend_schema(
        summary='get the common pains and diseaeses related to specific equipment',
        examples=Diseases
    )
    def post (self, request, equipment_pk, *args, **kwargs):
        try:
            diseases = request.data['diseases']
            for disease in diseases:
                disease_= {
                    'disease':disease,
                    'equipment':equipment_pk
                }
                serializer = self.get_serializer(data=disease_)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
            return Response({'success':'equipment limitations created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
limitationList = LimitationListAV.as_view()


class LimitationDetailsAV(generics.RetrieveDestroyAPIView):
    serializer_class = LimitationsSerializer
    queryset = Limitations.objects.all()
        
limitationDetails = LimitationDetailsAV.as_view()

@extend_schema(
    summary='get the diseases related to client'
)
class Client_diseasesListAV(generics.ListCreateAPIView):
    serializer_class = Client_DiseaseSerilaizer
    
    def get_queryset(self):
        client = Client.objects.get(user=self.request.user)
        return Client_Disease.objects.filter(client=client)
    
    @extend_schema(
    summary='add diseases related to client',
    examples = Diseases
)

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            with transaction.atomic():
                client = Client.objects.get(user = request.user.id)
                for disease in data['diseases']:
                    disease_ = {}
                    disease_['client'] = client.pk
                    disease_['disease'] = disease
                    serializer = self.get_serializer(data = disease_)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    

                return Response({'success':'diseases add successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
Client_diseases = Client_diseasesListAV.as_view()

@extend_schema(
    summary='delete specifc disease related to the client'
)
class Client_diseasesDetailsAV(generics.RetrieveDestroyAPIView):
    serializer_class = Client_DiseaseSerilaizer
    queryset=Client_Disease.objects.all()

    @extend_schema(
        summary='get specific diseases related to client '
    )
    def get(self,request,*args,**kwargs):
        try:
            client = Client.objects.get(user=self.request.user)        
            instance = Client_Disease.objects.get(client=client,id=self.kwargs['pk'])
            serializer=self.get_serializer(instance)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)
    
Client_diseasesDetails = Client_diseasesDetailsAV.as_view()
    