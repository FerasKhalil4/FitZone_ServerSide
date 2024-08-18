from django.urls import path
from .views import *

urlpatterns = [
    path('check/<int:branch_id>/',check_Session,name='check_session'),
    path('subscription/<int:branch_id>/',subscribtion_List,name='subscribtion_List'),
    path('subscription-details/<int:pk>/',subscribtion_details,name='subscribtion_details'),
    # path('hi/',hi)
]
