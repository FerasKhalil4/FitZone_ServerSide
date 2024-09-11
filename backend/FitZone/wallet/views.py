from rest_framework import generics, status
from rest_framework.response import Response
from .DataExample import *
from .serializers import *
from .models import Wallet
from points.models import Points
from drf_spectacular.utils import  extend_schema
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ClientFilter

def Check_points_offer():
    points = 0
    check_first_time = Points.objects.get(activity = 'First Time Activity').points
    check_wallet_refill = Points.objects.get(activity = 'Wallet Refill').points
    points = check_first_time + check_wallet_refill
    if points > 0 :
        return points
    return 0

class WalletListAPIView(generics.ListAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.filter(client__user__is_deleted=False)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClientFilter
    @extend_schema(
        summary='get all wallets',
    )
    def get(self, request, *args, **kwargs):
        try:
            return Response(self.get_serializer(self.filter_queryset(self.get_queryset()),many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
walletList = WalletListAPIView.as_view()


class WalletDetailsAV(generics.RetrieveUpdateAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.filter(client__user__is_deleted=False)
    @extend_schema(
        summary='get specific wallet',
    )
    def get(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data, status=status.HTTP_200_OK)
    @extend_schema(
        summary='update specific wallet',
        examples=wallet_update
        
    )
    def put(self,request,*args, **kwargs):
        try:
            with transaction.atomic():
                points = Check_points_offer()
                data = request.data
                if data['amount'] > 0 :
                    instance = self.get_object()
                    instance.balance = instance.balance + data['amount']
                    instance.save()
                    client = Client.objects.get(id=instance.client.pk)
                    user = request.user
                    employee = Employee.objects.get(user__username = user)
                    
                    deposit_data = {
                        'employee':employee.pk,
                        'amount':data['amount'],
                        'client':instance.client.pk,
                        'tranasaction_type':'add'
                    }
                    client.points += points
                    client.save()
                    
                    deposit_serializer = DepositSerilaizer(data=deposit_data)
                    deposit_serializer.is_valid(raise_exception=True)
                    deposit_serializer.save()
                else:
                    return Response({'error':'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({'message':'transaction completed'
                                 ,'data':self.get_serializer(self.get_object()).data,
                                 'deposit_data':deposit_serializer.data
                                 }
                                , status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

walletDetails = WalletDetailsAV.as_view()
    
    

    
