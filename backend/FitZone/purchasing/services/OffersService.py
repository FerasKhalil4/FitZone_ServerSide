from offers.models import *
from store.models import Supplements, Accessories , Meals
from store.serializers import ProductSerializer,SupplementsSerializer,AccessoriesSerializer,MealsSerializer

class OfferService():
    
    @staticmethod
    def retrieve_offer_products(obj):
        try:
            data = []
            price_offer = obj.price_offers
            
            for item in price_offer.objects.values():
                product = Branch_products.objects.get(pk=item['product_id'])
                  
                if product.amount > 0 and product.is_available:
                    
                    if product.product_type == 'Supplement':
                        supplement = Supplements.objects.filter(pk=product.product_id).first()
                        base_product =  SupplementsSerializer(supplement).data
                        
                    elif product.product_type == 'Accessory':
                        accessory = Accessories.objects.filter(pk=product.product_id).first()
                        base_product =  AccessoriesSerializer(accessory).data
                                
                    elif product.product_type == 'Meal':
                        meal = Meals.objects.filter(pk=product.product_id).first()
                        base_product =  MealsSerializer(meal).data
                        
                    base_product['amount_bought'] = item['number']
                    base_product['image'] = str(product.image_path)
                    data.append(base_product)

                else:
                    break
            return data
        except Exception as e:
            raise ValidationError(str(e))
        