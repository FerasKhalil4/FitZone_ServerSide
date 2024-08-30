from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('<int:branch_id>/',offersList,name ='offersList'),
    path('percentage/fee/<int:branch_id>/',feePercentageList , name = 'feePercentageList'),
    path('percentage/category/<int:branch_id>/',categoryPercentageList , name = 'feePercentageList'),
    path('percentage/class/<int:branch_id>/',classPercentageList,name='classPercentageList'),
    path('price/fee/<int:branch_id>/',feePriceOfferList,name ='feePriceOfferList'),
    path('price/products/<int:branch_id>/',productPriceOfferList,name ='feePriceOfferList'),
    path('percentage/<int:pk>/<int:branch_id>/',percentageDetails, name = 'percentageDetails'),
    path('price/<int:pk>/<int:branch_id>/',priceDetails, name = 'priceDetails'),
    path('destroy/<int:pk>/<int:branch_id>/',destroyOffer, name ='destroyOffer'), 
    re_path(r'store/(?P<branch_id>\d+)?/?$',percentage_offer_store,name='percentage_offer_store'),
]
