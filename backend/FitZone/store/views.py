from rest_framework import generics , status
from rest_framework.response import Response
from .models import * 
from .serializers import *
from .permissions import *
from gym.models import Employee, Shifts
from django.db import transaction
from points.models import Points
from .paginations import CustomPagination
import math 
        
def get_product_points(price):
    activity = Points.objects.get(activity="Product points percentage").points_percentage
    return math.ceil(price / activity)

def check_product_data(data):
    
        if ('product' in data and 'product_id' in data) :
            raise serializers.ValidationError({'message':'please provide either the product_id or the product'})
        
        if  'product' in data :
            prdouct_data = data.get('product')
            product_serializer = ProductSerializer(data=prdouct_data)
            if product_serializer.is_valid(raise_exception=True):
                product = product_serializer.save()
            product = product.pk
        elif 'product_id' in data :
            product = data.get('product_id')
        else :
                raise serializers.ValidationError( {'message': 'product_id is required if product is not provided'})
        
        return product
     
    
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
    
ProductList = ProductListAV.as_view()

class ProductDetailsAV(generics.RetrieveUpdateAPIView):
    queryset = Branch_products.objects.filter(is_available= True)
    serializer_class = Branch_productSerializer
    
    def get_object(self, pk):
        return Branch_products.objects.get(pk=pk)
    
    def get(self, request, pk, *args, **kwargs):
        try:
            
            object_ = self.get_object(pk)
            serializer = self.get_serializer(object_)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Branch_products.DoesNotExist:
            return Response({'message':'Prdouct does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    @transaction.atomic 
    def put(self, request, pk, *args, **kwargs):
        try:
            object_ = self.get_object(pk)
            
            serializer = self.get_serializer(object_, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response ({'message':(str(e))}, status=status.HTTP_400_BAD_REQUEST)

ProductDetail = ProductDetailsAV.as_view()



class Branch_productListAV(generics.ListAPIView):
    queryset = Branch_products
    serializer_class = Branch_productSerializer
    pagination_class = CustomPagination
    
    def get (self, request, pk, *args, **kwargs):
        try:
            branch_product = Branch_products.objects.filter(branch_id = pk)
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(branch_product,request)
            serializer =self.get_serializer(page,many=True)

            data_ = []
            
            for data in serializer.data:
                if data['product_type']== 'Supplement':
                    supplement_ = Supplements.objects.get(id = data['product_branch_id'])
                    serializer = SupplementsSerializer(supplement_)
                    branch_data = serializer.data
                    branch_data['branch_product_id'] = data['id']
                    data_.append(branch_data)
                    
                elif data['product_type']=='Accessory':
                    accessory = Accessories.objects.get(id = data['product_branch_id'])
                    serializer = AccessoriesSerializer(accessory)
                    branch_data = serializer.data
                    branch_data['branch_product_id'] = data['id']
                    data_.append(branch_data)
                    
                elif data['product_type']=='Meal':
                    meal = Meals.objects.get(id = data['product_branch_id'])
                    serializer = MealsSerializer(meal)
                    branch_data = serializer.data
                    branch_data['branch_product_id'] = data['id']
                    data_.append(branch_data)
                    

            return paginator.get_paginated_response(data_)        
        except Exception as e: 
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
Branch_productList = Branch_productListAV.as_view()



class AccessoriesListAV(generics.ListCreateAPIView):
    queryset = Accessories.objects.all()
    serializer_class =AccessoriesSerializer
    #get all the accessories of the product for the creation process
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            product = check_product_data(data)
            details_data = data.get('details')
            detailed_data = []
            check_redundency = []
            for color, details in details_data.items():
                for detail in details:
                    
                    detail['branch_id'] = data.get('branch_id')
                    detail['price']=data.get('price')
                    detail['points_gained'] =  get_product_points(data.get('price'))
                    detail['image_path'] = data.get('image_path')    
                                    
                    check_redundency.append((color,detail['amount'],detail['size']))
                    

                    
                    check = Accessories.objects.filter(product = product, size=detail['size'],color=color).first()
                    if check is not None :
                        accessory_instnace = check
                    else:
                        accessory_detail = {}
                        
                        accessory_detail ['color'] = color           
                        accessory_detail['size'] = detail.pop('size')    
                        accessory_detail['product_id'] = product 
                        
                        accessorySerializer = self.get_serializer(data=accessory_detail)  
                        accessorySerializer.is_valid(raise_exception=True)
                        accessory_instnace = accessorySerializer.save()                  
                        
                    check_data = Branch_products.objects.filter(product_id = accessory_instnace.pk,
                                                                branch = data.get('branch_id'),
                                                                product_type = 'Accessory'
                                                                )
                    if check_data.exists():
                        return Response({'message':'branch already has this accessory'}, status=status.HTTP_400_BAD_REQUEST)
                
                    detail['product_branch_id'] = accessory_instnace.pk
                    detail ['product_type'] = 'Accessory'
                    productBranch_serializer = Branch_productSerializer(data=detail)
                    productBranch_serializer.is_valid(raise_exception=True)
                    productBranch_serializer.save()
                    
                    detailed_data.append(productBranch_serializer.data)
                    
            if len(check_redundency) != len(set(check_redundency)):
                return Response({'message':'check on the accessory attributes there is redudant data'}, status = status.HTTP_400_BAD_REQUEST)
            
            return Response({"message":"product Created successfully",
                                "product_data":detailed_data
                                },status=status.HTTP_201_CREATED
                            )
        except Exception as e:
            raise serializers.ValidationError(str(e))
    
AcccessoriesList = AccessoriesListAV.as_view()


class SupplementsListAV(generics.ListCreateAPIView):
    
    queryset = Supplements.objects.all()
    serializer_class = SupplementsSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            data = request.data 
            product = check_product_data(data)
            details_data = data.get('details')
            details_data['branch_id'] = data.get('branch_id')
            details_data['points_gained'] =  get_product_points(details_data.get('price'))
            details_data['image_path'] = data.get('image_path')  
            
            # check_product_branch = check_redudncy_branch_product(product,data.get('branch_id'))
            check = Supplements.objects.filter(product = product, weight = data.get('weight'),flavor=data.get('flavor')).first()
            if check is not None:
                supplement_insntance = check
            else:
                supplement_details = data.get('supp_data')
                supplement_details['product_id'] = product
                supplement_details['supplement_category_id'] = supplement_details.pop('supplement_category_id', None)

                supplementSerializer = self.get_serializer(data=supplement_details)  
                supplementSerializer.is_valid(raise_exception=True)
                supplement_insntance = supplementSerializer.save()
                
            check_data = Branch_products.objects.filter(product_id = supplement_insntance.pk,
                                                                branch = data.get('branch_id'),
                                                                product_type = 'Supplement'
                                                                )
            if check_data.exists():
                return Response({'message':'branch already has this Supplement'}, status=status.HTTP_400_BAD_REQUEST)
                
            details_data['product_branch_id'] = supplement_insntance.pk
            details_data ['product_type'] = 'Supplement'
            productBranch_serializer = Branch_productSerializer(data=details_data)
            productBranch_serializer.is_valid(raise_exception=True)
            productBranch_serializer.save()
            return Response({"message":"product Created successfully",
                                "product_data":productBranch_serializer.data,
                                "supp_data":supplementSerializer.data
                                },status=status.HTTP_201_CREATED
                            )
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)

supplemetsList = SupplementsListAV.as_view()

class MealListAV(generics.ListCreateAPIView):
    queryset = Meals.objects.all()
    serializer_class = MealsSerializer
    @transaction.atomic
    def post(self, request,*args, **kwargs):
        try:
            data = request.data 
            product = check_product_data(data)
            details = data.get('details',{})
            details['branch_id'] = data.get('branch_id')
            details['points_gained'] =  get_product_points(details.get('price'))
            details['image_path'] = data.get('image_path')  
            
            # check_product_branch = check_redudncy_branch_product(product,data.get('branch_id'))
            
            meals = data.get('meals',{})
            meals['product_id'] = product
            
            mealSerializer = MealsSerializer(data=meals)
            mealSerializer.is_valid(raise_exception=True)
            meal_instance = mealSerializer.save()
            check_data = Branch_products.objects.filter(product_id = meal_instance.pk,
                                                                branch = data.get('branch_id'),
                                                                product_type = 'Meal'
                                                                )
            if check_data.exists():
                return Response({'message':'branch already has this Meal'}, status=status.HTTP_400_BAD_REQUEST)
                
            
            details['product_branch_id'] = meal_instance.pk
            details['product_type'] = "Meal"
            productBranch_serializer = Branch_productSerializer(data=details)
            productBranch_serializer.is_valid(raise_exception=True)
            productBranch_serializer.save()
            return Response({"message":"product Created successfully",
                                "product_data":productBranch_serializer.data,
                                "supp_data":mealSerializer.data
                                },status=status.HTTP_201_CREATED
                            )
        except Exception as e :
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
    
mealList = MealListAV.as_view()
            