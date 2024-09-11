from django.urls import path
from .views import rate_list,rate_create,trainer_rate_details,gym_rate_details,app_rate_details,feedback_list,feedback_details
urlpatterns = [
    path('',rate_list,name='rate_list'),
    path('create/',rate_create,name='rate_create'),
    path('gym/<int:branch_id>/',gym_rate_details,name='gym_rate_details'),
    path('trainer/<int:trainer_id>/',trainer_rate_details,name='trainer_rate_details'),
    path('<int:pk>/',app_rate_details,name='app_rate_details'),
    path('feedback/',feedback_list,name='feedback_list'),
    path('feedback/<int:pk>/',feedback_details,name='feedback_details')
    
    
]
