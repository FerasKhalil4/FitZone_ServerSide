from django.urls import path
from .views import *

urlpatterns = [
    path('<int:gym_id>/', postListAV, name='post-list'),
    path('<int:pk>/<int:gym_id>/', postDetailAV, name='post-detail'),
]