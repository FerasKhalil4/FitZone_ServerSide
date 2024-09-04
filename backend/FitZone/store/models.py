from typing import Any
from django.db import models
from gym.models import Branch
from django.db.models import UniqueConstraint
class Category(models.Model):    
    
    name = models.CharField(max_length=50 , unique = True )
    description = models.TextField(max_length=100,blank=True)
    
class Product(models.Model):
    
    category = models.ForeignKey(Category , on_delete=models.CASCADE , related_name="category")
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    is_deleted = models.BooleanField(default=False)
    brand = models.CharField(max_length=50, null=True)
    image_path = models.ImageField(upload_to='images/',null=True)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=('name','brand','category'), name='brand_category_name_constraint'),
        ]
class Supplements_Category(models.Model):
    
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    
    
class Accessories (models.Model):
    
    product = models.ForeignKey(Product , on_delete = models.CASCADE , related_name="accessory")
    color = models.CharField(max_length=50, null=True)
    size = models.CharField(max_length=50,null=True)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=('product','color','size'), name='product_color_size'),
        ]
class Meals(models.Model):
    
    product = models.OneToOneField(Product , on_delete = models.CASCADE , related_name="meals")
    protein = models.FloatField(default=0.0,null=True)
    carbs = models.FloatField(default=0.0,null=True)
    calories = models.FloatField(default=0.0,null=True)
    fats = models.FloatField(default=0.0,null=True)
    used_for = models.CharField(max_length=50, blank = True)
    
class Supplements(models.Model):
    
    supplement_category = models.ForeignKey(Supplements_Category,
                                            on_delete = models.CASCADE , 
                                            related_name="supplemetns")
    product = models.ForeignKey(Product , on_delete = models.CASCADE , related_name="supplemetns")
    protein = models.FloatField(default=0.0,null=True)
    carbs = models.FloatField(default=0.0,null=True)
    calories = models.FloatField(default=0.0,null=True)
    caffeine = models.FloatField(default=0.0,null=True)
    weight = models.FloatField(default=0.0,null=True)
    flavor = models.CharField(blank=True, max_length=50)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=('product','weight','flavor'), name='product_weight_flavor'),
        ]
    
    
class Branch_products(models.Model):
    
    branch = models.ForeignKey(Branch , on_delete= models.CASCADE,related_name="product")
    product_id = models.PositiveBigIntegerField(blank=True)
    product_type = models.CharField(blank = True, max_length=50)
    amount = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    price = models.FloatField(default=0.0)
    points_gained = models.IntegerField(default=0)
    image_path = models.ImageField(upload_to='images/' , null = True)
    
    def delete(self, *args, **kwargs):
        if self:
            self.is_available = False
            self.save()
    
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=('branch','product_id','product_type'), name='branch_product_constraint'),
        ]
    
        
        