from django.urls import path
from .views import( public_store,private_store,purchase_private_store,
                    purchase_public_store,product_details,private_product_details,purchases,purchases_details,check_purchasings,add_products,update_purchase)
urlpatterns = [
    path('store/public/',public_store,name='public_store'),
    path('store/private/<int:branch_id>/',private_store,name='private_store'),  
    path('products/private/<int:branch_id>/',purchase_private_store,name='purchase_private_store'),
    path('products/public/',purchase_public_store,name='purchase_public_store'),
    path('products/<int:pk>/',product_details,name='product_details'),
    path('private/products/<int:pk>/<int:branch_id>/',private_product_details,name='private_product_details'),
    path('client/history/',purchases,name='purchases'),
    path('client/history/<int:pk>/',purchases_details,name='purchases_details'),
    path('edit/<int:pk>/',check_purchasings,name='check_purchasings'),
    path('products/add/<int:pk>/',add_products,name='add_products'),
    path('amount/products/<int:pk>/',update_purchase,name='update_purchase'),
]
