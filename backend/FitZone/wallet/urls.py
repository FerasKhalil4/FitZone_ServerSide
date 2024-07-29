from django.urls import path
from .views import * 
urlpatterns = [
    path('',walletList,name='walletList'),
    path('<int:pk>/',walletDetails,name='walletDetails'), 
]
