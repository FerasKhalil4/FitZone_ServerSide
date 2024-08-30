from rest_framework import serializers 
from .models import * 
from gym.models import Gym
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
    

class AccessoriesStoreSerializer(serializers.ModelSerializer):
    accessory_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    class Meta:
        model = Accessories
        fields = ['accessory_id','size','color']
        
class MealStoreSerializer(serializers.ModelSerializer):
    meal_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    class Meta:
        model = Meals
        fields = ['meal_id', 'protein','calories','carbs','fats','used_for']
class SupplemntStoreSerializer(serializers.ModelSerializer):
    supplement_category = Supplements_CategorySerilaizer(read_only=True)
    supplement_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    class Meta:
        model = Supplements
        fields = ['supplement_id','protein','calories','carbs','caffeine',
                    'flavor','weight','supplement_category']
        
class PublicStoreSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(source='id',read_only=True)
    category= CategorySerializer(read_only=True)
    accessories = AccessoriesStoreSerializer(source='accessory',read_only=True,many=True)
    meals_ = MealStoreSerializer(source='meals',read_only=True)
    supplements_ = SupplemntStoreSerializer(source='supplemetns',read_only=True,many=True) 
    product_branch_availability = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['product_id', 'category','name', 'description','brand'
                  ,'brand','accessories','meals_','supplements_','product_branch_availability']
    
    
    def append_data(self,branch_data,instance,branch):
        try:
            if f'gym_{branch.branch.gym.pk}' not in branch_data[instance.pk]:
                branch_data[instance.pk][f'gym_{branch.branch.gym.pk}'] = {
                    'gym_name': branch.branch.gym.name,
                    'gym_id' : branch.branch.gym.pk,
                    'products_data' : [] 
                }
                
            return branch_data[instance.pk][f'gym_{branch.branch.gym.pk}']['products_data'].append(
                                    {
                                    "branch_product_id":branch.pk,
                                    'branch':branch.branch.pk,
                                    'price':branch.price,
                                    'image':str(branch.image_path),
                                    'points_gained':branch.points_gained,
                                    'branch_address': f"{branch.branch.city} - {branch.branch.street} - {branch.branch.address} " 
                                        
                                    }
                                    )
        except Exception as e:
            raise serializers.ValidationError(str(e))
                
    def get_product_branch_availability(self,obj):

        try:
            branch_data = {}
            if obj.category.pk == 1:
                supplements = Supplements.objects.filter(product=obj.pk)
                for supplement in supplements:
                    branch_= Branch_products.objects.filter(product_id = supplement.pk ,
                                                            product_type = 'Supplement',
                                                            branch__gym__allow_public_products = True)
                    if len(branch_) > 0:
                        branch_data[supplement.pk] = {}
                        for branch in branch_:
                            self.append_data(branch_data,supplement,branch)
                            
            if obj.category.pk == 2:
                meals = Meals.objects.filter(product=obj.pk)
                for meal in meals:
                    branch_= Branch_products.objects.filter(product_id = meal.pk , 
                                                            product_type = 'Meal',
                                                            branch__gym__allow_public_products = True
                                                            )
                    if len(branch_) > 0:
                        branch_data[meal.pk] =  {}
                        for branch in branch_:
                            self.append_data(branch_data,meal,branch)

            if obj.category.pk == 3:
                accessories = Accessories.objects.filter(product=obj.pk)
                for accessory in accessories:
                    branch_= Branch_products.objects.filter(product_id = accessory.pk , 
                                                            product_type = 'Accessory',
                                                            branch__gym__allow_public_products = True
                                                            )
                    if len(branch_) > 0:
                        branch_data[accessory.pk] =  {} 
                        for branch in branch_:
                            self.append_data(branch_data,accessory,branch)
            return branch_data
                
        except Exception as e:
            raise serializers.ValidationError(str(e))

class PrivateStoreSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['products']
            
    
    
    def get_retieved_data(self,instance,instance_data):
        instance.pop('product',None)
        return {
        'product_data':instance,
        'branch_product_id':instance_data.pk,
        'product_amount':instance_data.amount,
        'price':instance_data.price,
        'image_path':str(instance_data.image_path),
        'points_gained':instance_data.points_gained,
        'branch':instance_data.branch.pk,
        'branch_address': f"{instance_data.branch.city} - {instance_data.branch.street} - {instance_data.branch.address}" 
        }
        
    def get_products_data(self,product,branch):
        product_data = []
        print(product.category.name)

        if product.category.name == 'Supplement':
            
            supplements = Supplements.objects.filter(product=product.pk)
            print(supplements)
            for supplement in supplements:
                try:
                    serializer = SupplementsSerializer(supplement).data
                    instance = Branch_products.objects.get(product_id = supplement.pk,branch=branch,is_available=True)
                    product_data.append(self.get_retieved_data(serializer,instance))
                except Branch_products.DoesNotExist:
                    pass
            
            
        elif product.category.name == 'Meal':
            
            meals =Meals.objects.filter(product=product.pk)
            for meal in meals:
                try:
                    serializer = MealsSerializer(meal).data
                    instance = Branch_products.objects.get(product_id = meal.pk,branch=branch,is_available=True)
                    product_data.append(self.get_retieved_data(serializer,instance))
                except Branch_products.DoesNotExist:
                    pass
                
        elif product.category.name == 'Accessory':
            
            accessories = Accessories.objects.filter(product=product.pk)
            for accessory in accessories:
                try:
                    serializer = AccessoriesSerializer(accessory).data
                    instance = Branch_products.objects.get(product_id = accessory.pk,branch=branch,is_available=True)
                    product_data.append(self.get_retieved_data(serializer,instance))
                except Branch_products.DoesNotExist:
                    pass
                
        return product_data
    
    
    def get_products(self, obj):
        try:
            products_data = self.get_products_data(obj,self.context.get('branch'))
            
            return products_data
            
        except Exception as e:
            raise serializers.ValidationError(str(e))