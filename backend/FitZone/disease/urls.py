from django.urls import path
from .views import *

urlpatterns = [
    
    path('', disease_list,name = 'disease_list'),
    path('limitations/<int:equipment_pk>/',limitationList,name = 'limitations_list'),
    path('limitations-details/<int:pk>/',limitationDetails,name='limitation_details'),
    path('client/',Client_diseases,name='Client_diseases'),
    path('client/<int:pk>/',Client_diseasesDetails,name='Client_diseasesDetails')
]

