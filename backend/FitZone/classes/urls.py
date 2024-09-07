from django.urls import path, re_path
from .views import *
urlpatterns = [
    path('<int:branch_id>/', classesListAV , name ='classListAV'),
    path('<int:branch_id>/<int:pk>/',classesDetailAV , name = 'classDetailAV'),
    path('schedule/<int:pk>/',Class_ScheduleList, name = 'Class_ScheduleList'),
    path('schedule-details/<int:pk>/',Class_ScheduleDetails, name = 'Class_ScheduleDetaisl'),
    path('client/<int:branch_id>/',client_classes,name='client_classes'),
    path('register/',client_registration,name='client_registration'),
    path('register/<int:pk>/',client_registration_details,name='client_registration_details'),
    
]
