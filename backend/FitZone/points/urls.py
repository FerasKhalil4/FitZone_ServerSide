from django.urls import path 
from .views import *

urlpatterns = [
    path('', pointList, name = 'pointsList'),
    path('<int:pk>/', pointsDetails, name = 'pointsDetails'),
]
