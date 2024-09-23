from django.urls import path
from  .views import diet_helper
urlpatterns = [
    path('',diet_helper,name='diet_helper')
]
