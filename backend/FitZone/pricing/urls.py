from django.urls import path
from .views import update_gym_subscription_pricing, update_branch_products_pricing, update_class_registration_pricing

urlpatterns = [
    path('gym/subscription/<int:pk>/',update_gym_subscription_pricing, name = 'update_gym_subscription_pricing'),
    path('branch/products/<int:pk>/',update_branch_products_pricing, name = 'update_branch_products_pricing'),
    path('branch/classes/<int:pk>/',update_class_registration_pricing, name = 'update_class_registration_pricing')
]
