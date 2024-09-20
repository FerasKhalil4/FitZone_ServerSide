from django.urls import path
from .views import *
 
urlpatterns = [
    path('clients/',clientlist, name='clientsList'),
    path('clients/<int:pk>/',approveClients, name='approveClients'),
    path('client/plan/<int:client_id>/',ClientTrainingPlanRetrieve,name='ClientTrainingPlanRetrieve'),
    path('groups/',trainerGroupsList,name='trainerGroupsList'),
    path('groups/<int:pk>/',TrainerGroupsDetail,name='trainerGroups'),
    path('clients/details/<int:client_id>/',client_details,name='client_details'),
    path('profile/',trainer_profile,name='trainer_profile'),
    path('subscription/',trainer_subscriptions,name = 'trainer_subscriptions'),
    path('subscription/<int:pk>/',trainer_subs_details,name='trainer_subs_details'),
    path('client/groups/<int:trainer_id>/',client_groups,name='client_groups'),
    path('client/current/',CurrentTrainerClient,name = 'CurrentTrainerClient'),
]
