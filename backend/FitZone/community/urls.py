from django.urls import path
from .views import *

urlpatterns = [
    path('', postListAV, name='post-list'),
    path('<int:pk>/', postDetailAV, name='post-detail'),
]