from django.urls import path
from .views import public_store,private_store,purchase_private_store,purchase_public_store,product_details,private_product_details

urlpatterns = [
    path('store/public/',public_store,name='public_store'),
    path('store/private/<int:branch_id>/',private_store,name='private_store'),  
    path('products/private/<int:branch_id>/',purchase_private_store,name='purchase_private_store'),
    path('products/public/',purchase_public_store,name='purchase_public_store'),
    path('products/<int:pk>/',product_details,name='product_details'),
    path('private/products/<int:pk>/<int:branch_id>/',private_product_details,name='private_product_details')
]
