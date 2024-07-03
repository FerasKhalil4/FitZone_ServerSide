from django.urls import path
from .views import *
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    
    path('registration/',Registration , name = 'registration_client'),
    path('login/',Login , name = 'login'),
    path('TokenObtainPairView/',TokenObtainPairView.as_view(),name = 'TokenObtainPairView'),
    path('refresh/',TokenRefreshView.as_view(),name ='refresh'),
    path('verify/',TokenVerifyView.as_view(),name ='verify'),
    path('profile/client/' , client_profile , name = 'client_profile'),
    path('employee-edit/<int:pk>/',employeeDetailAV , name = 'employeeListAV'),
    
    # path('profile/' , user_profile , name = 'user_profile'),
]
