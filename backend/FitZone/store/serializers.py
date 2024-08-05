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
        fields = ['id','name','description']
        





class ProductSerializer (serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_data = CategorySerializer(source = 'category',read_only=True)
    image_path = serializers.FileField(required=False)
    class Meta:
        model = Product 
        
        fields = ['id','name','description','category','category_data','brand','image_path'] 
class AccessoriesSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = Accessories
        fields = ['product','size','color']
class CreateProductSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),write_only=True,required=False)
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    category = serializers.PrimaryKeyRelatedField (queryset=Category.objects.all(),write_only=True,required=False)
    brand = serializers.CharField(required=False)
    
    
    class Meta:
        model = Product
        fields = ['name','description','category','brand','image_path','product_id']   
    def valdiate(self, data):
        if ('product' in data and 'product_id' in data) :
            raise serializers.ValidationError({'message':'please provide either the product_id or the product'})
        if  'product' in data :
            pass
        elif 'product_id' in data :
            pass
        else :
                raise serializers.ValidationError( {'message': 'product_id is required if product is not provided'})
        if 'name' not in data:
            pass
        return data

        
class Branch_productSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(source='branch',queryset=Branch.objects.filter(is_active=True),write_only=True)
    product_branch_id = serializers.IntegerField(source = 'product_id')
    branch_product_id = serializers.IntegerField(source = 'id',read_only=True)
    class Meta:
        model = Branch_products
        
        fields = ['branch_product_id','amount','price','points_gained','is_available','image_path'
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
    
            
class Supplements_CategorySerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Supplements_Category
        fields = '__all__'
    
     
    
class SupplementsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    supplement_category = Supplements_CategorySerilaizer(read_only=True)
    supplement_category_id = serializers.PrimaryKeyRelatedField(
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

    class Meta:
        model = Meals
        fields =['product', 'protein','calories','carbs','fats','used_for']
    
        
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

    
    


class MealRequestSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),required=False)
    meals = MealsSerializer()
    image_path = serializers.ImageField(source='product.image_path',required=False)
    
    class Meta:
        model = Meals
        fields = ['product','product_id','meals','image_path']
    
    
    def create(self, validated_data):
        
        product_data = validated_data.pop('product', None)
        meals_data = validated_data.pop('meals', None)
        product_id = validated_data.pop('product_id', None)

        if product_data:
            product = Product.objects.create(**product_data)
            meals_data['product_id'] = product.pk
            
        elif product_id :
            meals_data['product_id'] = product_id.pk
            
        meal_instance = Meals.objects.create(**meals_data)


        return meal_instance
    
class SupplementsRequestSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),required=False)
    supplements = SupplementsSerializer()
    image_path = serializers.ImageField(source='product.image_path',required=False)
    
    class Meta:
        model = Meals
        fields = ['product','product_id','supplements','image_path']
    
    
        
    def create(self, validated_data):
        product_data = validated_data.get('product',None)
        product_id = validated_data.get('product_id',None)
        supplement_data = validated_data.get('supplements')
        

        
        if len(product_data) == 1:
            product_data = None
        if product_data:
            product = Product.objects.create(**product_data)
            product = product.pk
            
        elif product_id :
            product = product_id.pk
        check = Supplements.objects.filter(product = product, weight = supplement_data.get('weight'),flavor=supplement_data.get('flavor')).first()
        if check is not None:
            supplement_instance = check
                    
        
        else:
            supplement_data['product_id'] = product
            supplement_data['supplement_category_id'] =supplement_data.pop('supplement_category_id').pk
            supplement_instance = Supplements.objects.create(**supplement_data)
        return supplement_instance


class SupplementsRequestSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),required=False)
    supplements = SupplementsSerializer()
    image_path = serializers.ImageField(source='product.image_path',required=False)
    
    class Meta:
        model = Meals
        fields = ['product','product_id','supplements','image_path']
    
    
        
    def create(self, validated_data):
        product_data = validated_data.get('product',None)
        product_id = validated_data.get('product_id',None)
        supplement_data = validated_data.get('supplements')
        
        if product_data:
            product = Product.objects.create(**product_data)
            product = product.pk
            
        elif product_id :
            product = product_id.pk
        check = Supplements.objects.filter(product = product, weight = supplement_data.get('weight'),flavor=supplement_data.get('flavor')).first()
        if check is not None:
            supplement_instance = check
                    
        
        else:
            supplement_data['product_id'] = product
            supplement_data['supplement_category_id'] =supplement_data.pop('supplement_category_id').pk
            supplement_instance = Supplements.objects.create(**supplement_data)
        return supplement_instance
    
    
    
class AccessoryRequestSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),required=False)
    accessory = AccessoriesSerializer(many=True)
    image_path = serializers.ImageField(source='product.image_path',required=False)
    
    class Meta:
        model = Meals
        fields = ['product','product_id','accessory','image_path']
    
    
    def create(self, validated_data):
        product_data = validated_data.pop('product', None)
        accessories_data = validated_data.pop('accessory', None)
        product_id = validated_data.pop('product_id', None)
        if product_data:
            product = Product.objects.create(**product_data)           
            
        elif product_id :
            product = product_id
        
        accessories_retrieved = []
        for accessory in accessories_data:
            accessory['product'] = product
            accessory_instance = Accessories.objects.create(**accessory)
            accessories_retrieved.append(accessory_instance)
        return accessories_retrieved
class BranchProductCreateSerializer(serializers.ModelSerializer):
    branch_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    image_path = serializers.FileField(required=False)
    class Meta:
        model = Branch_products
        
        fields = ['amount','price','points_gained','is_available','image_path',
                  'branch_id','product_type','product_id']
        
    def validate_image_path(self, value):
        if not value:
            return None
        
        if not hasattr(value, 'content_type'):
            raise serializers.ValidationError("Invalid image file.")
        
        valid_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        
        if value.content_type not in valid_mime_types:
            raise serializers.ValidationError("Unsupported image file type.")
        
        return value
        
    def create (self, data):
        data['branch_id'] = data['branch_id'].pk
        
        return Branch_products.objects.create(**data)        