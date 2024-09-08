from django.urls import path
from .views import index,client_diet
urlpatterns = [
    path('',index,name='index'),
    path('client/plan/',client_diet,name='client_diet')
]
