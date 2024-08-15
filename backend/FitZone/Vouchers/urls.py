from django.urls import path
from .views import voucherList, voucherDetails, redeem, ActiveVouchers
urlpatterns = [
    path('', voucherList, name = 'voucherlist'),
    path('<int:pk>/',voucherDetails ,name='voucherDetails'),
    path('redeem/',redeem,name='redeem'),
    path('active/',ActiveVouchers, name ='ActiveVouchers')
]
