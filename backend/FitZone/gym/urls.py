from django.urls import path 
from .views import *



urlpatterns = [
    path('',GymListCreate, name='GymListCreate'),
    path('<int:pk>/',GymRetrieveUpdateDestroy, name='GymListCreate'),
    path('branch/<int:pk>/' , branchAv , name = 'BrancListCreate'),
    path('manager/' , managergymAV , name = 'ManagerGymList'),
    path('branch-detail/<int:pk>/' , branchDetailAV , name ='branchDetail'),
    path('employee/<int:branch_id>/',employeeListAV , name = 'employeeListAV'),
    path('trainer/<int:branch_id>/',trainerListAV , name = 'TrainerList'),
    path('shifts/<int:pk>/' , shiftCreateAV , name = 'shiftCreateAV'),
    path('shifts/update/<int:pk>/',shiftUpdateAV, name= 'shiftUpdateAV'),
    path('fee/<int:gym_id>/',fee_list,name='fee_list'),
    path('clients/',get_gyms_clients,name='get_gyms_clients'),
    
    
]