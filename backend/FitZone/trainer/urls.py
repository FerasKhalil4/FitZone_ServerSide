from django.urls import path
from .views import *
 
urlpatterns = [
    path('clients/',clientlist, name='clientsList'),
    path('clients/<int:pk>/',approveClients, name='approveClients'),
    
    
]
