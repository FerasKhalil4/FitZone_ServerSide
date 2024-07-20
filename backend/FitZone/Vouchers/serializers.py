from rest_framework import  serializers
from .models import  *

class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ['id','name','points_required','number_of_days','is_deleted']
        