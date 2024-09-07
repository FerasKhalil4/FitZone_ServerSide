from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import *
from gym.permissions import admin_permissions
from django.db import transaction
from drf_spectacular.utils import extend_schema

class VoucherListAV(generics.ListCreateAPIView):
    queryset = Voucher.objects.filter(is_deleted=False)
    serializer_class = VoucherSerializer
    # permission_classes = [admin_permissions]
    
voucherList = VoucherListAV.as_view()

class VoucherDetailsAV(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voucher.objects.filter(is_deleted=False)
    serializer_class = VoucherSerializer
    permission_classes = [admin_permissions]
    
    
voucherDetails = VoucherDetailsAV.as_view()


class RedeemListAV(generics.ListCreateAPIView):
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all()
    
    @extend_schema(
        summary='get all clients vouchers'
    )
    
    def get(self, request, *args, **kwargs):
        try:
            now = datetime.now().date()
            
            client = Client.objects.get(user=request.user.pk)
            voucher = Redeem.objects.filter(client=client.pk )
            
            return Response(self.get_serializer(voucher,many=True).data,status=status.HTTP_200_OK)
        
        except Exception or  Client.DoesNotExist as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
                
    @extend_schema(
        summary='Redeem client points to vouchers'
    )
    
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                client = Client.objects.get(user=request.user.pk)
                request.data['client'] = client.pk
                return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
redeem = RedeemListAV.as_view()

class CurrentVouchersAV(generics.RetrieveAPIView):
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all()
    
    @extend_schema(
        summary='get the current active voucher'
    )
    
    def get(self, request, *args, **kwargs):
        try:
            now = datetime.now().date()
            
            client = Client.objects.get(user=request.user.pk)
            voucher = Redeem.objects.filter(client=client.pk,start_date__lte = now, expired_date__gte = now )
            
            return Response(self.get_serializer(voucher,many=True).data,status=status.HTTP_200_OK)
        
        except Exception or  Client.DoesNotExist as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
ActiveVouchers = CurrentVouchersAV.as_view()