from django.urls import path 
from .views import *



urlpatterns = [
    path('',GymListCreate, name='GymListCreate'),
    path('<int:pk>/',GymRetrieveUpdateDestroy, name='GymListCreate'),
    path('branch/<int:pk>/' , branchAv , name = 'BrancListCreate'),
    path('manager/' , managergymAV , name = 'ManagerGymList'),
    path('branch-detail/<int:pk>/' , branchDetailAV , name ='branchDetail'),
    path('employee/<int:pk>/',employeeListAV , name = 'employeeListAV'),
    path('trainer/',trainerListAV , name = 'TrainerList'),
    
]