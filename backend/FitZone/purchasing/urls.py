from django.urls import path
from .views import public_store,private_store

urlpatterns = [
    path('store/public/',public_store,name='public_store'),
    path('store/private/<int:branch_id>/',private_store,name='private_store'),  
]
