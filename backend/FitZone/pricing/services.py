from gym.models import Registration_Fee, Branch, Gym
from store.models import Branch_products
from classes.models import Classes
from django.db import transaction
from django.db.models.query import QuerySet


def get_type_of_pricing (percentage:float,type_of_pricing:str) -> float:
    return {
        'add': percentage,
        'deduct': -percentage  
    }[type_of_pricing]
        
        
def get_new_pricing(item:float, percentage_value:float) -> float:
       return item + (item * (percentage_value / 100))

def get_gym_registration_fees(gym:Gym) -> QuerySet:
    fees = Registration_Fee.objects.filter(gym=gym)
    if fees.exists():
        return fees
    else:
        raise ValueError('no fees exists in this gym')

def get_branch_products(branch:Branch) -> QuerySet:
    products = Branch_products.objects.filter(branch=branch, branch__is_active=True, branch__has_store=True)
    if products.exists():
        return products
    else:
        raise ValueError('no products exist in this branch')

def get_classes(branch:Branch) -> QuerySet:
    classes = Classes.objects.filter(branch=branch, branch__is_active=True)
    if classes.exists():
        return classes  
    else:
        raise ValueError('no classes exist in this branch')


def apply_new_prices(queryset:QuerySet, percentage_value:float,field_name:str) -> None:
    
        try:
            with transaction.atomic():
                for item in queryset:
                    price_field = getattr(item, field_name)
                    new_price = get_new_pricing(price_field, percentage_value)
                    setattr(item, field_name, new_price)
                    item.save()
        except Exception as e:
            raise ValueError(str(e))

    
def update_pricing(get_items_func:QuerySet, searched_place:object, data:dict, field_name:str) -> None:
    items = get_items_func(searched_place)
    try:
        new_percentage_value = get_type_of_pricing(data['percentage'], data['type_of_pricing'])
    except KeyError:
        raise ValueError('Invalid operation type')
    apply_new_prices(items, new_percentage_value, field_name)
    
    
def update_gym_pricings(data:dict) -> None:
    update_pricing(get_gym_registration_fees, data['gym'], data, 'fee')


def update_branch_products_pricings(data:dict) -> None:
    update_pricing(get_branch_products, data['branch'], data, 'price')

    
def update_classes_registration_pricings(data:dict) -> None:
    update_pricing(get_classes, data['branch'], data, 'registration_fee')
