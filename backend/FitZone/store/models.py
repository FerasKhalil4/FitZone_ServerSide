from django.db import models
from gym.models import Branch

class Category(models.Model):    
    
    name = models.CharField(max_length=50 , unique = True )
    description = models.TextField(max_length=100,blank=True)
    
class Product(models.Model):
    
    category = models.ForeignKey(Category , on_delete=models.CASCADE , related_name="category")
    name = models.CharField(max_length=50 , unique=True)
    description = models.TextField(max_length=100)
    is_deleted = models.BooleanField(default=False)

class Supplements_Category(models.Model):
    
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    
    
class Accessories (models.Model):
    
    product = models.ForeignKey(Product , on_delete = models.CASCADE , related_name="accessory")
    color = models.CharField(max_length=50, null=True)
    size = models.CharField(max_length=50,null=True)
    
class Meals(models.Model):
    
    product = models.ForeignKey(Product , on_delete = models.CASCADE , related_name="meals")
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
    
class Branch_products(models.Model):
    
    branch = models.ForeignKey(Branch , on_delete= models.CASCADE,related_name="product")
    product_id = models.PositiveBigIntegerField(blank=True)
    product_type = models.CharField(blank = True, max_length=50)
    amount = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    price = models.FloatField(default=0.0)
    points_gained = models.IntegerField(default=0)
    image_path = models.ImageField(upload_to='images/' , null = True)


    