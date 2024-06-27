from django.urls import path
from .views import *
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('registration/',Registration , name = 'registration_client'),
    path('login/',Login , name = 'login'),
    path('TokenObtainPairView/',TokenObtainPairView.as_view(),name = 'TokenObtainPairView'),
    path('refresh/',TokenRefreshView.as_view(),name ='refresh'),
    path('verify/',TokenVerifyView.as_view(),name ='verify'),
    path('profile/client/' , client_profile , name = 'client_profile'),
    # path('profile/' , user_profile , name = 'user_profile'),
]
