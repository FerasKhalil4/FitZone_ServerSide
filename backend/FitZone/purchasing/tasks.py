from __future__ import unicode_literals,absolute_import
from .models import Purchase
from datetime import datetime
from celery import shared_task
from dateutil.relativedelta import relativedelta
from store.models import Branch_products
from offers.models import Offer
@shared_task
def delete_expired_purchases():
    purchases = Purchase.objects.filter(total=0)
    now = datetime.now().date()
    
    for purchase in purchases:
        flag = False
        products = purchase.products.values()
        for product in products:
            duration_allowed = Branch_products.objects.get(pk=product['product_id']).branch.gym.duration_allowed 
            duration_allowed = 0 if duration_allowed is None else duration_allowed
            
            check = purchase.created_at.date() + relativedelta(days=duration_allowed)
            if now > check :
                flag = True
        offers = purchase.PriceOffers.values()
        for offer in offers :
            print(offer)
            duration_allowed = Offer.objects.get(price_offers__pk = offer['price_offer_id']).branch.gym.duration_allowed 
            duration_allowed = 0 if duration_allowed is None else duration_allowed
            check = purchase.created_at.date() + relativedelta(days=duration_allowed)
            if now > check :
                flag = True
        
        if flag :
            purchase.is_deleted = True
            purchase.save()
            
    