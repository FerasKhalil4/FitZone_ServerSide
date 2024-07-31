from rest_framework import generics, status
from rest_framework.response import Response
from .DataExample import *
from .serializers import *
from .models import Wallet
from drf_spectacular.utils import  extend_schema
from django.db import transaction

class WalletListAPIView(generics.ListAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.filter(client__user__is_deleted=False)
    @extend_schema(
        summary='get all wallets',
    )
    def get(self, request, *args, **kwargs):
        try:
            return Response(self.get_serializer(self.get_queryset(),many=True).data, status=status.HTTP_200_OK)
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
                data = request.data
                if data['amount'] > 0 :
                    instance = self.get_object()
                    instance.balance = instance.balance + data['amount']
                    instance.save()
                    
                    user = request.user
                    employee = Employee.objects.get(user__username = user)
                    deposit_data = {
                        'employee':employee.pk,
                        'amount':data['amount'],
                        'client':instance.client.pk
                    }
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
    
    

    
