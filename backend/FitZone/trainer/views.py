from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from .serialziers import *
from .filters import Client_TrainerFilter
from .DataExamples import *
import datetime
from dateutil.relativedelta import relativedelta
    

class ClientsListAV(generics.ListAPIView):
    serializer_class = Client_TrainerSerializer
    queryset = Client_Trainer.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = Client_TrainerFilter
    @extend_schema(
            summary = 'get the clients registered with the trainer'
        )
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            trainer = Trainer.objects.get(employee__user = user)
            qs = self.filter_queryset(self.get_queryset())
            qs = qs.filter(trainer=trainer)
            serializer = self.get_serializer(qs,many=True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status =status.HTTP_400_BAD_REQUEST)
            
clientlist = ClientsListAV.as_view()


class ApproveClientsAV(generics.RetrieveUpdateAPIView):
    serializer_class = Client_TrainerSerializer
    queryset = Client_Trainer.objects.exclude(registration_status = 'rejected')

    @extend_schema(
        summary = 'get specific pending client'
    )
    def get(self, request, *args, **kwargs):
        try:
            client = self.get_object()
            user = request.user
            trainer = Trainer.objects.get(employee__user = user)     
            if trainer != client.trainer :
                return Response({'error':'invalid client'}, status=status.HTTP_400_BAD_REQUEST)       
            return Response(self.get_serializer(client).data , status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status = status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        summary = 'approve or reject specific pending client',
        examples=approve_client
    )
    def put(self, request, *args, **kwargs):
        try:
            with transaction.atomic():                
                data=request.data
                instance = self.get_object()
                if instance.registration_status == 'accepted':
                    return Response({'error':'you cant update the status of this client'},status = status.HTTP_400_BAD_REQUEST)
                user = request.user
                trainer = Trainer.objects.get(employee__user = user)     
                
                if trainer != instance.trainer :
                    return Response({'error':'invalid client'}, status=status.HTTP_400_BAD_REQUEST)   
                if data['registration_status'] != 'rejected' and data['rejection_reason'] is not None:
                    return Response({'error':'check on the rejection Note please'}, status=status.HTTP_400_BAD_REQUEST)
                if data['registration_status'] != 'rejected':
                    start_date = datetime.datetime.now().date()
                    end_date = start_date + relativedelta(months=1)
                    data['start_date'] = start_date
                    data['end_date'] = end_date
                serializer = self.get_serializer(instance, data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':'client status updated'},status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status = status.HTTP_400_BAD_REQUEST)

approveClients = ApproveClientsAV.as_view()