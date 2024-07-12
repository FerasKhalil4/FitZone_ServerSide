from django.urls import path
from .views import *
urlpatterns = [
    path('equipment/',Equipment_lisAtV , name='equipementsListAV'),
    path('equipment/<int:pk>',Equipment_detailAV,name='equipment_detail'),
    path('',diagram_listAV,name='diagrams_list'),
    path('<int:pk>/',diagram_detailsAV, name = 'diagram_detail'),
]
