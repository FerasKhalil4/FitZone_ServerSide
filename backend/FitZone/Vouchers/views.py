from rest_framework import generics, status
from .serializers import *
from gym.permissions import admin_permissions
class VoucherListAV(generics.ListCreateAPIView):
    queryset = Voucher.objects.filter(is_deleted=False)
    serializer_class = VoucherSerializer
    permission_classes = [admin_permissions]
    
voucherList = VoucherListAV.as_view()

class VoucherDetailsAV(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voucher.objects.filter(is_deleted=False)
    serializer_class = VoucherSerializer
    permission_classes = [admin_permissions]
    
    
voucherDetails = VoucherDetailsAV.as_view()