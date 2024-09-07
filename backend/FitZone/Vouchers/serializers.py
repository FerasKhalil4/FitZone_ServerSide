from rest_framework import  serializers
from .models import  *

class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ['id','name','points_required','number_of_days','restrict_num_using','discount']
        
class RedeemSerializer(serializers.ModelSerializer):
    voucher_date = VoucherSerializer(source='voucher',read_only=True)
    code = serializers.CharField(read_only=True)
    points_used = serializers.IntegerField(read_only=True)
    class Meta:
        model = Redeem
        fields = ['id','client','voucher','times_used','points_used','expired_date','code','start_date','voucher_date']
        
    def create(self,validated_data):
        return super().create(validated_data)        