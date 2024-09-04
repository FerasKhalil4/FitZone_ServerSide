from ..models import * 
from wallet.models import Wallet , Wallet_Deposit
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import transaction


class Delete_Purchase():
    
    @staticmethod 
    def check_cut_percentage(gym,item_total) -> float:
        total = 0
        if gym.cut_percentage is not None:
            gym_percentage_cut = 100 - gym.cut_percentage
            gym_percentage_cut = (gym_percentage_cut / 100) 
        else:
            gym_percentage_cut = 1
        # print(f'gym percentege cut{gym_percentage_cut}')
        # print(f'product total {item_total}')
        if 1 > gym_percentage_cut > 0:
            # print(f'old total{total}')
            
            total += item_total * gym_percentage_cut
            # print(f'new total{total}')
            
        elif gym_percentage_cut == 0:
            # print(f'old total{total}')
            total += item_total
            # print(f'new total{total}')
        
        elif gym_percentage_cut == 1:
            pass
        return total
    
    @staticmethod 
    def delete_products(product) -> None:
        try:
            branch_product = Branch_products.objects.get(pk=product.product.pk,is_available=True)
            branch_product.amount += product.amount
            branch_product.save()
        except Branch_products.DoesNotExist:
            pass
        
    
    @staticmethod
    def delete_offers(offer) -> None:
        try:
            for item in offer.price_offer.objects.values():
                branch_product = Branch_products.objects.get(pk=item['product_id'],is_available=True)
                # print(f'previous amount{branch_product.amount}')
                branch_product.amount += offer.amount
                # print(f'new amount{branch_product.amount}')
                
                branch_product.save()
                
        except Price_Offer.DoesNotExist:
            pass
        
    @staticmethod 
    def retrieve_money(client,total) -> None:
        wallet = Wallet.objects.get(client=client)
        wallet.balance += total
        wallet.save()
        Wallet_Deposit.objects.create(
            client = client,
            amount = total,
            tranasaction_type = 'retrieve'
        )
        return True
        
    @staticmethod
    def delete_purchase(obj) -> bool:
        
        # print(obj)
        try:
            with transaction.atomic():
                
                obj.is_deleted = True
                obj.save()
                
                products = Purchase_Product.objects.filter(purchase=obj.pk,is_deleted=False)
                offers = Purchase_PriceOffer.objects.filter(purchase=obj.pk,is_deleted=False)
                now = datetime.now().date()
                client =  obj.client
                total = 0
                flag = True
                for product in products:
                    prodcut_total = product.product_offer_total if 0 < product.product_offer_total < product.product_total  else product.product_total
                    
                    product.is_deleted = True
                    product.save()
                    Delete_Purchase.delete_products(product)
                    
                    product_gym = product.product.branch.gym
                    
                    if product_gym.allow_retrival:
                            allowed_date = obj.created_at.date() + relativedelta(days=product_gym.duration_allowed)
                            
                            if  now <= allowed_date:
                                    total += Delete_Purchase.check_cut_percentage(product_gym,prodcut_total)
                            else:
                                raise ValueError('cannot delete this purchase as it is not allowed by the bought products store policy')                    
                for offer in offers:
                    
                    offer_total = offer.offer_total
                    offer.is_deleted = True
                    offer.save()
                    
                    Delete_Purchase.delete_offers(offer)
                    
                    offer_gym = offer.price_offer.offer.branch.gym
                    
                    if offer_gym.allow_retrival:
                            allowed_date = obj.created_at.date() + relativedelta(days=offer_gym.duration_allowed)
                            
                            if  now <= allowed_date:
                                    total += Delete_Purchase.check_cut_percentage(offer_gym,offer_total)
                            else:
                                raise ValueError('cannot delete this purchase as it is not allowed by the bought products store policy')                    
                                
                            
                # print(f'new total {total}')
                Delete_Purchase.retrieve_money(client,total)
                
        except Exception as e:
            raise ValueError(str(e))
    