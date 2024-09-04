from ..models import *
from offers.models import Percentage_offer
from datetime import datetime 
from .private_store_service import PrivateStoreService

class PublicPurchaseService():
    
    @staticmethod
    def use_price_offer(price_offer,purchasing_instance,now):
        price_offer_total = 0
        for offer in price_offer:
            price_offer_total = PrivateStoreService.price_offers_proccessing(offer['offer_id'],now,offer['amount'],offer['branch_id'],purchasing_instance,price_offer_total)
        print(f'price offer total {price_offer_total}')
        return price_offer_total
        
    @staticmethod
    def purchase_management(products,vouchers,price_offer_total,purchasing_instance):
        total = price_offer_total
        offered_total = price_offer_total
        points_gained = 0 
        percentage_offer_data = {}
        now = datetime.now().date()
        for product in products:
            flag = False
            branch_id = product['branch_id'].pk
            if branch_id not in percentage_offer_data:
                percentage_offer = percentage_offer_data[branch_id] = PrivateStoreService.check_percentage_offers(branch_id,now)
            else:
                percentage_offer = percentage_offer_data[branch_id]
            products_total = 0
            product_offered_total = 0
            branch_product = product['branch_product_id']
            amount = product['amount']
            product_type = branch_product.product_type 
            
            points_gained += branch_product.points_gained * amount
            products_total = branch_product.price * amount

            if branch_product.amount > amount:
                branch_product.amount -= amount 
            else :
                raise ValueError(f'there insufficient amount of the product {branch_product.pk} at gym {branch_product.branch.gym.name} in branch {branch_product.branch.address}')

            branch_product.save()
            
            if percentage_offer != {}:
                product_offered_total = PrivateStoreService.use_percentage_offer(product_type,percentage_offer,branch_product,products_total,product_offered_total)
            
            total += products_total  
            offered_total += product_offered_total if product_offered_total != 0 else products_total
            
            print('check in the public store')
            print(total)
            for item in purchasing_instance.products.values():
                if item['product_id'] == product['branch_product_id'].pk:
                    try:
                        purchase_product = Purchase_Product.objects.get(product_id=item['product_id'],purchase_id=purchasing_instance.pk,is_deleted=False)
                        flag = True
                        
                        print('=========================================')
                        print(purchase_product.product_total)
                        print(purchase_product.product_offer_total)
                        print(purchase_product.amount)
                        print('------------------------------')
                        print(products_total)
                        print(product_offered_total)
                        print(product['amount'])
                        print('------------------------------')
                        
                        
                        purchase_product.product_total += products_total
                        purchase_product.product_offer_total += product_offered_total
                        purchase_product.amount += product['amount']
                        
                        print(purchase_product.amount)
                        print(purchase_product.product_total)
                        print(purchase_product.product_offer_total)
                        
                        print('=========================================')
                        
                        purchase_product.save()
                        break
                    except Purchase_Product.DoesNotExist:
                        print(f'excption was risen {flag}')
                        pass
                    
            if not flag:
                Purchase_Product.objects.create(
                    purchase = purchasing_instance,
                    product = product['branch_product_id'],
                    amount = product['amount'],
                    product_total = products_total,
                    product_offer_total = product_offered_total                
                )
        if vouchers != 0:
            offered_total = PrivateStoreService.use_voucher(vouchers,offered_total)
        return {
            'total': total,
            'offered_total': offered_total,
            'points':points_gained,
            }
    
    @staticmethod
    def Purchase(data):
        products = data.pop('products')
        vouchers_code = data.pop('vouchers',[])
        voucher_discount = 0
        client = data['client']
        now = datetime.now().date()
        price_offer = data.pop('price_offers',[])
        price_offer_total = 0
        
        purchasing_instance = Purchase.objects.create(
            client=client,
            is_public=True
        )
        
        if price_offer != []:
            price_offer_total = PublicPurchaseService.use_price_offer(price_offer,purchasing_instance,now)
            
        if vouchers_code != []:
            voucher_discount = PrivateStoreService.check_voucher(client,vouchers_code,now)
        
        total = PublicPurchaseService.purchase_management(products,voucher_discount,price_offer_total,purchasing_instance)
        client.points += total['points']
        client.save()
        
        purchasing_instance.total = total['total']
        purchasing_instance.offered_total = total['offered_total'] if total['offered_total'] != total['total'] else None
        purchasing_instance.save()
        PrivateStoreService.wallet_cut(total,client)
        return purchasing_instance