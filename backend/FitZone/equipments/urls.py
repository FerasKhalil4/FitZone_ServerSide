from django.urls import path
from .views import *
urlpatterns = [
    path('equipment/',Equipment_lisAtV , name='equipementsListAV'),
    path('equipment/<int:pk>/',Equipment_detailAV,name='equipment_detail'),
    path('<int:branch_id>/',diagram_listAV,name='diagrams_list'),
    path('<int:pk>/<int:branch_id>/',diagram_detailsAV, name = 'diagram_detail'),
    path('disease/', disease_list,name = 'disease_list'),
    path('limitations/<int:equipment_pk>/',limitationList,name = 'limitations_list'),
    path('limitations-details/<int:pk>/',limitationDetails,name='limitation_details'),
]
