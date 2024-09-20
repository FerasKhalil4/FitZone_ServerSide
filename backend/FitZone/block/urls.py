from django.urls import path
from .views import Blocklist,BlockDetails
urlpatterns = [
    path('',Blocklist,name='BlockList'),
    path('<int:pk>/',BlockDetails,name='BlockDetails')
]
