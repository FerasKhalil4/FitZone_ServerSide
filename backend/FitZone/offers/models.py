from django.db import models
from gym.models import Registration_Fee
from classes.models import Class_Scheduel
from store.models import Branch_products, Category, Supplements_Category, Branch

class Offer(models.Model):
    name = models.CharField(max_length=60,blank=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    image_path = models.ImageField(upload_to="images/", blank=True)
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

class Price_Offer(models.Model):
    offer = models.OneToOneField(Offer, on_delete=models.CASCADE, related_name='price_offers')
    price = models.PositiveIntegerField(default=0)

class ObjectHasPriceOffer(models.Model):
    offer = models.ForeignKey(Price_Offer, on_delete=models.CASCADE, related_name='objects')
    product = models.ForeignKey(Branch_products, on_delete=models.CASCADE, related_name='offers',null=True)
    fee = models.ForeignKey(Registration_Fee, on_delete=models.CASCADE, related_name='price_offers',null=True)
    number = models.IntegerField(default=0)


    