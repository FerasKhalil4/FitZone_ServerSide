from django.urls import path
from .views import *
urlpatterns = [
    path('', classesListAV , name ='classListAV'),
    path('<int:pk>/',classesDetailAV , name = 'classDetailAV'),
]
