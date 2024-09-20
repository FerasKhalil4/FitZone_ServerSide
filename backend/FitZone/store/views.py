from rest_framework import generics , status
from rest_framework.response import Response
from .models import * 
from .serializers import *
from .permissions import *
from points.models import Points
from .paginations import CustomPagination
from django.db import transaction
import json
import math 
from django.core.files.storage import default_storage

class StoreMixin():
    
    def get_product_points(self,price):
        activity = Points.objects.get(activity="Purchasing").points_percentage
        return math.ceil(price / activity)
        # Purchasing
                
    def category_data(self,serializer_category,product):
        serializer_category['amount'] = product.amount
        serializer_category['price'] = product.price
        serializer_category['image_path'] = str(product.image_path) or ""
        serializer_category['is_available'] = product.is_available
        serializer_category['branch_product_id'] = product.pk
        
        return serializer_category
     
    def create_branch_product(self, details, branch_id, instance, product_type):

        details['branch_id'] = branch_id
        details['points_gained'] = self.get_product_points(details.get('price'))
        details['product_id'] = instance.pk
        details['product_type'] = product_type

        check_data = Branch_products.objects.filter(product_id = instance.pk,
                                                            branch =branch_id,
                                                            product_type = product_type
                                                            )
        if check_data.exists():
            return Response({'message':'branch already has this Meal'}, status=status.HTTP_400_BAD_REQUEST)
        product_serializer =BranchProductCreateSerializer(data=details)
        product_serializer.is_valid(raise_exception=True)
        product_serializer.save()
        print(instance)
        print(product_serializer.data)
        return True
    
    def check_product(self,validated_data):
        if 'product' in validated_data and 'product_id' in validated_data:
            raise serializers.ValidationError('Product already in request body')
        return validated_data
    
    def check_store(self,branch_id) -> None:
        if Branch.objects.get(pk=branch_id).has_store:
            pass 
        else :
            raise ValueError('this branch does not have a store')
        

    

class CategoryAV(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
categoryList = CategoryAV.as_view()

class SupplementCategory(generics.ListAPIView):
    queryset = Supplements_Category.objects.all()
    serializer_class = Supplements_CategorySerilaizer

supplementCategoryList = SupplementCategory.as_view()
    
class ProductListAV(generics.ListAPIView):
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        
        return Product.objects.filter(is_deleted=False, category = self.kwargs.get('category_id'))
    
ProductList = ProductListAV.as_view()

class ProductDetailsAV(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch_products.objects.filter(is_available= True)
    serializer_class = Branch_productSerializer
    
    
    def get(self, request, pk, *args, **kwargs):
        try:
            object_ = self.get_object()
            serializer = self.get_serializer(object_)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Branch_products.DoesNotExist:
            return Response({'message':'Prdouct does not exist'}, status=status.HTTP_404_NOT_FOUND)
        

    def put(self, request, pk, *args, **kwargs):
        try:
            with transaction.atomic():
                object_ = self.get_object()
                serializer = self.get_serializer(object_, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response ({'message':(str(e))}, status=status.HTTP_400_BAD_REQUEST)

ProductDetail = ProductDetailsAV.as_view()



class Branch_productListAV(StoreMixin,generics.ListAPIView):
    queryset = Branch_products
    serializer_class = Branch_productSerializer
    pagination_class = CustomPagination
    
    def get (self, request, pk, *args, **kwargs):
        
        try:
            branch_product = Branch_products.objects.filter(branch_id = pk).order_by('id')
            # paginator = self.pagination_class()
            # page = paginator.paginate_queryset(branch_product,request)

            data_ = []
            
            for data in branch_product:
                print(data.product_type)
                if data.product_type== 'Supplement':
                    print('start')
                    supplement_ = Supplements.objects.get(id = data.product_id)
                    
                    serializer = SupplementsSerializer(supplement_)
                    
                    branch_data = serializer.data
                    
                    branch_data['branch_product_id'] = pk
                    # branch_data['image_path'] = image_path
                    print(branch_data)
                    # print(str(branch_data['image_path']))
                    # branch_data['image_path'] = str(branch_data['image_path'])
                    branch_data = self.category_data(branch_data , data)
                    data_.append(branch_data)
                    print('end')
                    
                elif data.product_type=='Accessory':
                    
                    accessory = Accessories.objects.get(id = data.product_id)
                    serializer = AccessoriesSerializer(accessory)
                    branch_data = serializer.data
                    branch_data['branch_product_id'] = pk
                    # branch_data['image_path'] = str(branch_data['image_path'])
                    
                    branch_data = self.category_data(branch_data , data)
                    # branch_data['image_path'] = image_path

                    data_.append(branch_data)
                    # return paginator.get_paginated_response(data_)        
                    
                elif data.product_type=='Meal':
                    
                    meal = Meals.objects.get(id = data.product_id) 
                    serializer = MealsSerializer(meal)
                    branch_data = serializer.data
                    branch_data['branch_product_id'] = pk
                    print(branch_data)
                    # branch_data['image_path'] = str(branch_data['image_path'])

                    
                    branch_data = self.category_data(branch_data , data)
                    # branch_data['image_path'] = image_path

                    data_.append(branch_data)  
            print(data_)
            return Response (data_,status=status.HTTP_200_OK)        
        except Exception as e: 
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
Branch_productList = Branch_productListAV.as_view()



class AccessoriesListAV(StoreMixin,generics.ListCreateAPIView):
    queryset = Accessories.objects.all()
    serializer_class =AccessoriesSerializer
    
    def post(self, request,branch_id, *args, **kwargs):
        try:
            with transaction.atomic():
                self.check_store(branch_id)
                image = request.FILES.get('image_path',None)
                
                data = request.data.dict()
                self.check_product(data)
                if 'product_id' in data :
                    data.pop('image_path',None)
                if isinstance(data.get('product'), str):
                    data['product'] = json.loads(data['product'])
                if isinstance(data.get('accessory'), str):
                    data['accessory'] = json.loads(data['accessory'])
                    
                serializer = AccessoryRequestSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                accessory_instances = serializer.save()
                
                if isinstance(data['details'], str):
                    details = json.loads(data['details'])
                if image is not None:
                    details['image_path'] = image
                
                for instance in accessory_instances:
                    for item in data['accessory']:
                        print(item)
                        if item['color'] == instance.color and item['size'] == instance.size:
                            details['amount'] = item['amount']
                            self.create_branch_product(details, branch_id, instance, 'Accessory')
                    

                return Response({"message": "Accessories processed successfully."}, status=status.HTTP_201_CREATED)

            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
AcccessoriesList = AccessoriesListAV.as_view()


class SupplementsListAV(StoreMixin,generics.ListCreateAPIView):
    
    queryset = Supplements.objects.all()
    serializer_class = SupplementsSerializer
    
    def post(self, request,branch_id, *args, **kwargs):
        try:
            # check(data,image = image) 
            with transaction.atomic():
                self.check_store(branch_id)
                
                image = request.FILES.get('image_path',None)
                data = request.data.dict()
                
                
                self.check_product(data)
                
                if 'product_id'  in data :
                    data.pop('image_path',None)
                
                if isinstance(data.get('product'), str):
                    data['product'] = json.loads(data['product'])
                if isinstance(data.get('supplements'), str):
                    data['supplements'] = json.loads(data['supplements'])
                    
                serializer = SupplementsRequestSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                supplement_instance = serializer.save() 
                
                if isinstance(data['details'], str):
                    details = json.loads(data['details'])
                if image is not None:
                    details['image_path'] = image
                    
                self.create_branch_product(details, branch_id, supplement_instance, 'Supplement')
                
                return Response({"message":"product Created successfully"
                                    },status=status.HTTP_201_CREATED
                                )
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)

supplemetsList = SupplementsListAV.as_view()


class MealListAV(StoreMixin,generics.ListCreateAPIView):
    queryset = Meals.objects.all()
    serializer_class = MealsSerializer

    def post(self, request, branch_id, *args, **kwargs):
        try:
            with transaction.atomic():
                self.check_store(branch_id)
                
                image = request.FILES.get('image_path',None)
                data = request.data.dict()
                
                if 'product_id'  in data :
                    data.pop('image_path',None)
                
                if isinstance(data.get('product'), str):
                    data['product'] = json.loads(data['product'])
                if isinstance(data.get('meals'), str):
                    data['meals'] = json.loads(data['meals'])
                    
                serializer = MealRequestSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                meal_instance = serializer.save()
                
                if isinstance(data['details'], str):
                    details = json.loads(data['details'])
                if image is not None:
                    details['image_path'] = image
                    
                self.create_branch_product(details, branch_id, meal_instance, 'Meal')
                
                return Response({"message": "Product created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

mealList = MealListAV.as_view()

        
class CategoryProductsListAV(StoreMixin,generics.ListAPIView):
    serializer_class = Branch_productSerializer
    queryset = Branch_products.objects.all()
    pagination_class = CustomPagination
    def get(self, request,category_id,branch_id, *args, **kwargs):
        try:
            
            category = Category.objects.get(id=category_id)
            products = Branch_products.objects.filter(product_type = category.name, branch_id = branch_id).order_by('id')
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(products,request)
            data_retrieved = []
            if category.name == 'Supplement':
                for product in page:
                    supplemetns = Supplements.objects.get(pk=product.product_id)
                    serializer_category = SupplementsSerializer(supplemetns).data     
                    serializer_category = self.category_data(serializer_category , product)
                    serializer_category['image_path'] = str(serializer_category['image_path'])
                    data_retrieved.append(serializer_category)
                    
                return paginator.get_paginated_response(data_retrieved)
            elif category.name == 'Accessory':
                for product in page:
                    accessories = Accessories.objects.get(pk=product.product_id)
                    serializer_category = AccessoriesSerializer(accessories).data
                    serializer_category = self.category_data(serializer_category , product)
                    serializer_category['image_path'] = str(serializer_category['image_path'])
                    data_retrieved.append(serializer_category)
                    
                return paginator.get_paginated_response(data_retrieved)
            elif category.name == 'Meal':
                for product in page:
                    meals = Meals.objects.get(pk=product.product_id)
                    serializer_category = MealsSerializer(meals).data
                    serializer_category = self.category_data(serializer_category , product)
                    serializer_category['image_path'] = str(serializer_category['image_path'])
                    data_retrieved.append(serializer_category)
                return paginator.get_paginated_response(data_retrieved)
            
            
        except Category.DoesNotExist:
            return Response({'error':'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Branch_products.DoesNotExist:
            return Response({"error": "Branch products not found"}, status=status.HTTP_404_NOT_FOUND)
        except Supplements.DoesNotExist:
            return Response({"error": "Supplement not found"}, status=status.HTTP_404_NOT_FOUND)
        except Accessories.DoesNotExist:
            return Response({"error": "Accessory not found"}, status=status.HTTP_404_NOT_FOUND)
        except Meals.DoesNotExist:
            return Response({"error": "Meal not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
    
CategoryProductsList = CategoryProductsListAV.as_view()
