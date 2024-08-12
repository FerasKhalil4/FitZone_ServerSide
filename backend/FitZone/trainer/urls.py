from django.urls import path
from .views import *
 
urlpatterns = [
    path('clients/',clientlist, name='clientsList'),
    path('clients/<int:pk>/',approveClients, name='approveClients'),
    path('client/plan/<int:client_id>/',ClientTrainingPlanRetrieve,name='ClientTrainingPlanRetrieve'),
    path('groups/',trainerGroupsList,name='trainerGroupsList'),
    path('groups/<int:pk>/',TrainerGroupsDetail,name='trainerGroups')
]
