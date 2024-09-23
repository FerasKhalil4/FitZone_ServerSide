from django.urls import path
from .views import *

urlpatterns = [
    path('admin/users/',admin_user_stats,name='admin_user_stats'),
    path('admin/gym/',admin_gym_stats,name='admin_gym_stats'),
    path('admin/vouchers/',admin_vouchers_stats,name='admin_vouchers_stats'),
    path('manager/branches/',manager_branches_stats,name='manager_branches_stats'),
    path('manager/branches/activity/',get_manager_branches_activity_stats,name='manager_branches_activity_stats'),
    path('manager/products/',get_manager_products_stats,name='manager_branches_activity_stats'),
    path('manager/classes/',get_manager_classes_stats,name='get_manager_classes_stats'),
    
]
