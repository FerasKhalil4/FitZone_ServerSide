from django.urls import path
from .views import *
urlpatterns = [
    path('<int:branch_id>/', classesListAV , name ='classListAV'),
    path('<int:branch_id>/<int:pk>/',classesDetailAV , name = 'classDetailAV'),
    path('schedule/<int:pk>/',Class_ScheduleList, name = 'Class_ScheduleList'),
    path('schedule-details/<int:pk>/',Class_ScheduleDetails, name = 'Class_ScheduleDetaisl'),
    
]
