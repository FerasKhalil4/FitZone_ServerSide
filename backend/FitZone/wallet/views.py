from rest_framework import generics, status
from rest_framework.response import Response
from .DataExample import *
from .serializers import WalletSerializer
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
            print(self.get_q)
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
                serializer = self.get_serializer(self.get_object(), data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

walletDetails = WalletDetailsAV.as_view()
    
    

    
