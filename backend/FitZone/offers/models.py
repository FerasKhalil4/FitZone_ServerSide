from django.db import models
from gym.models import Registration_Fee
from classes.models import Class_Scheduel
from store.models import Branch_products, Category, Supplements_Category, Branch
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import datetime
class Offer(models.Model):
    name = models.CharField(max_length=60,blank=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    is_deleted = models.BooleanField(default=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='offers')
    
    def delete(self):
        if self.is_deleted != True:
            self.is_deleted = True
            self.save()

class Percentage_offer(models.Model):
    offer = models.OneToOneField(Offer, on_delete=models.CASCADE, related_name='percentage_offers')
    percentage_cut = models.PositiveIntegerField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="offer", null=True)
    supp_category = models.ForeignKey(Supplements_Category, on_delete=models.CASCADE, related_name="offer", null=True)
    fee = models.ForeignKey(Registration_Fee, on_delete=models.CASCADE, related_name='percentage_offers', null=True)
    class_id = models.ForeignKey(Class_Scheduel, on_delete=models.CASCADE, related_name='percentage_offers', null=True)
    
    def check_offer(self):
        
        overlapped_query = (Q(
            offer__start_date__lte = self.offer.start_date,
            offer__end_date__gt=self.offer.start_date,
        )|Q(
            offer__start_date__lt = self.offer.end_date,
            offer__end_date__gte=self.offer.end_date,
        )|Q(
            offer__start_date__gte = self.offer.start_date,
            offer__end_date__lte=self.offer.end_date,
        )) & Q(
            offer__branch = self.offer.branch
        )
        
        category_query = overlapped_query &Q(
            category = self.category,
            category__isnull = False 
        ) & (Q(
                supp_category__isnull = True
            ) | Q(
                supp_category = self.supp_category,
                )
            )
        
        query = category_query |Q(
            fee = self.fee,
            fee__isnull = False
        ) | Q(
            class_id = self.class_id,
            class_id__isnull = False
        )
        if  Percentage_offer.objects.filter(query).exists():
            raise ValidationError('you cannot create a Percentage offer now where this item already has an offer')
        return 

        
    def clean(self) -> None:
        super().clean()
        check = sum (attr is not None for attr in [self.category,self.class_id,self.fee])        
        if check != 1:
            raise ValidationError('the offer is supposed to be for one item')
        if (self.category is None and self.supp_category is not None )or (self.category.pk != 1 and self.supp_category is not None ) :
            print(self.category != 1 and self.supp_category is not None)
            raise ValidationError('the offer for supp category should ne for category')

        
    def save(self,*args, **kwargs):
        self.clean()
        self.check_offer()
        super().save(*args, **kwargs)
 
class Price_Offer(models.Model):
    offer = models.OneToOneField(Offer, on_delete=models.CASCADE, related_name='price_offers')
    price = models.PositiveIntegerField(default=0)

class ObjectHasPriceOffer(models.Model):
    offer = models.ForeignKey(Price_Offer, on_delete=models.CASCADE, related_name='objects')
    product = models.ForeignKey(Branch_products, on_delete=models.CASCADE, related_name='offers',null=True)
    fee = models.ForeignKey(Registration_Fee, on_delete=models.CASCADE, related_name='price_offers',null=True)
    number = models.IntegerField(default=0)
    
    def clean(self):
        super().clean()
        
        check = sum(attr is not None for attr in [self.product, self.fee])
        if check != 1:
            raise ValidationError('the offer is supposed to be for one item')
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    