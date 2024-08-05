from django.urls import path
from .views import *

urlpatterns = [
    path('category/',categoryList , name="categoryList"),   
    path ('supplement/category/',supplementCategoryList,name="supplementCategoryList"),
    path('product/category/<int:category_id>/',ProductList , name="productList"),
    path('product/accessories/<int:branch_id>/',AcccessoriesList , name="AcccessoriesList"),
    path('product/supplements/<int:branch_id>/',supplemetsList , name="supplementsList"),
    path('product/<int:pk>/',ProductDetail,name = 'ProductDetail'),
    path('branch/products/<int:pk>/',Branch_productList,name = 'BranchesList'),
    path('product/meals/<int:branch_id>/',mealList,name='mealsList'),
    path('category/products/<int:category_id>/<int:branch_id>/',CategoryProductsList,name = 'CategoryProducts'),
    # path('data/',create_.as_view())
    
]

 