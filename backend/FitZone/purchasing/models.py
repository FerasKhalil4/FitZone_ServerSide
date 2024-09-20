from django.db import models
from store.models import Branch_products
from offers.models import Price_Offer,Offer,ObjectHasPriceOffer
from user.models import Client
from django.db.models import UniqueConstraint,Q
class Purchase(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE,related_name='purchases')
    total = models.FloatField(default=0.0)
    offered_total = models.FloatField(default=0.0,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    number_of_updates = models.IntegerField(default=0)
    
    def save(self,*args, **kwargs):
        print('models')
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        if self:
            self.is_deleted = True
            self.save()
        
class Purchase_Product(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE,related_name='products')
    product = models.ForeignKey(Branch_products, on_delete=models.CASCADE,related_name='purchases')
    amount = models.PositiveIntegerField(default=0)
    product_total = models.FloatField(default=0.0)
    product_offer_total = models.FloatField(default=0.0)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=('purchase','product') ,name='purchase_products_constraint',
                             condition=Q(
                                    is_deleted = False   
                                )
                            )
        ]

class Purchase_PriceOffer(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE,related_name='PriceOffers')
    price_offer = models.ForeignKey(Price_Offer,on_delete=models.CASCADE,related_name='purchases')
    amount = models.PositiveIntegerField(default=0)
    offer_total = models.FloatField(default=0.0)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=('purchase','price_offer') ,name='purchase_price_offer_constraint',
                                                          condition=Q(
                                    is_deleted = False   
                                )
                            ),
        ]

