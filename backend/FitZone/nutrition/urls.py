from django.urls import path
from .views import *
urlpatterns = [
    path('client/plan/',NutritionPlanList,name='NutritionPlanList'),
    path('plan/<int:client_id>/',NutritionPlanCreate,name="NutritionPlanCreate"),
    path('plan/status/',UpdatePlanStatus,name = 'UpdatePlanStatus'),
    path('meal/create/<int:meals_type_id>/',MealsCreate,name = 'MealsCreate'),
    path('meal/details/<int:pk>/',MealsDetails,name='MealsDetails'),
    path('meal/type/create/<int:schdeule_id>/',MealsTypeCreate, name='MealsTypeCreate'),
    path('meal/type/destroy/<int:pk>/',MealsTypeDelete, name = 'MealsTypeDelete')
    
]
