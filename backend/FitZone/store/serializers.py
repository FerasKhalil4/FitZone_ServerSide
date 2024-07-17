from rest_framework import serializers 
from .models import * 
from gym.seriailizers import BranchSerializer


def validate_field(field, value):
    if value < 0 :
        raise serializers.ValidationError(f'{field} must be positive Value')
    return value

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['name','description']

class ProductSerializer (serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_data = CategorySerializer(source = 'category',read_only=True)
    class Meta:
        model = Product 
        
        fields = ['id','name','description','category','category_data']    

class Supplements_CategorySerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Supplements_Category
        fields = '__all__'
    
# class VariantSerializer(serializers.ModelSerializer):
#     product_id = serializers.PrimaryKeyRelatedField(source = 'product',
#                                                     queryset=Product.objects.all(),
#                                                     write_only=True)
#     supplement_category =Supplements_CategorySerilaizer(read_only=True)
#     supplement_category_id = serializers.PrimaryKeyRelatedField(source='supplement_category',
#                                                                 queryset=Supplements_Category.objects.all(),
#                                                                 write_only=True,required = False)
#     product = ProductSerializer(read_only=True)
#     class Meta:
#         model=Variants
#         fields= ['calories','weight','protein','carbs','caffeine',
#                  'supplement_category','flavor','product_id','supplement_category_id'
#                  ,'color','size','product']           


class AccessoriesSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(source = 'product',
                                                    queryset=Product.objects.all()
                                                    ,write_only=True)

    class Meta:
        model = Accessories
        fields = ['product', 'product_id','size','color']
     
    
class SupplementsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(source = 'product',
                                                    queryset=Product.objects.all()
                                                    ,write_only=True)
    supplement_category = Supplements_CategorySerilaizer(read_only=True)
    supplement_category_id = serializers.PrimaryKeyRelatedField(source = "supplement_category",
                                                                queryset=Supplements_Category.objects.all()
                                                                ,write_only=True)
    
    class Meta:
        model = Supplements
        fields =['product', 'product_id', 'protein','calories','carbs','caffeine',
                 'flavor','weight','supplement_category','supplement_category_id']
        
        def validate_weight(self,value):
           return validate_field('weight',value)
           
        def validate_protein(self,value):
            return validate_field('protein',value)
            
        def validate_calories(self,value):
          return validate_field('calories',value)
      
        def validate_carbs(self,value):
           return validate_field('carbs',value)
       
        def validate_caffeine(self,value):
         return validate_field('caffeine',value)
     
     
class MealsSerializer(serializers.ModelSerializer):
    
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(source = 'product',
                                                    queryset=Product.objects.all()
                                                    ,write_only=True)
    
    class Meta:
        model = Meals
        fields =['product', 'product_id', 'protein','calories','carbs','fats','used_for']
    
        
        def validate_weight(self,value):
           return validate_field('weight',value)
           
        def validate_protein(self,value):
            return validate_field('protein',value)
            
        def validate_calories(self,value):
          return validate_field('calories',value)
      
        def validate_carbs(self,value):
           return validate_field('carbs',value)
       
        def validate_fats(self,value):
         return validate_field('fats',value)

            
class Branch_productSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(source='branch',queryset=Branch.objects.filter(is_active=True),write_only=True)
    product_branch_id = serializers.IntegerField(source = 'product_id')
    class Meta:
        model = Branch_products
        
        fields = ['id','amount','price','points_gained','is_available','image_path'
                  ,'branch','branch_id','product_branch_id','product_type']
        
    unique_together = ('product_type', 'product_id')
    def validate(self,data):
        amount = data.get('amount',None)        
        price = data.get('price',None)
        if amount  < 0 :
            raise serializers.ValidationError({'error':'please check on the amount field they should be positive values'})
        if  price < 0 :
            raise serializers.ValidationError({'error':'please check on the price field they should be positive values'})
            
        return data