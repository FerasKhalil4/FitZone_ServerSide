from django.urls import path
from .views import voucherList, voucherDetails
urlpatterns = [
    path('', voucherList, name = 'voucherlist'),
    path('<int:pk>',voucherDetails ,name='voucherDetails' )
]
