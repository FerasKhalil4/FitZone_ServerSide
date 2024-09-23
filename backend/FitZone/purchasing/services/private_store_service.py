from ..models import *
from offers.models import Percentage_offer
from datetime import datetime 
from wallet.models import Wallet,Wallet_Deposit
from store.models import Supplements
from Vouchers.models import  Redeem
class PrivateStoreService():
    
    @staticmethod
    def check_voucher(client,vouchers,now):
        voucher_discount = 0
        for voucher in vouchers:
            try:
                voucher_instance = Redeem.objects.get(client=client,
                                                      code=voucher,
                                                      start_date__lte = now,
                                                      expired_date__gte = now,
                                                    )
                if voucher_instance.voucher.restrict_num_using >= voucher_instance.times_used + 1:
                    voucher_instance.times_used += 1
                    voucher_instance.save()
                    voucher_discount += voucher_instance.voucher.discount
            except Redeem.DoesNotExist:
                pass
        return voucher_discount
            
    @staticmethod
    def check_percentage_offers(branch,now):
        offers = {
            'supplement_category':{},
            'Supplement':None,
            'Accessory':None,
            'Meal':None
        }
        percentage_offer = Percentage_offer.objects.filter(offer__is_deleted=False,
                                                        offer__start_date__lte=now,
                                                        offer__end_date__gte = now,
                                                        offer__branch = branch,
                                                        category__isnull=False
                                                    )
        for offer in percentage_offer:
            if offer.supp_category is not None:
                offers['supplement_category'][offer.supp_category.name] = offer.percentage_cut
            else:
                offers[offer.category.name] = offer.percentage_cut
        return offers 
    
    
    @staticmethod 
    def price_offers_proccessing(offer_id,now,amount,branch,purchasing_instance,price_offer_total):
            offer_total = 0
            flag = False
            try:
                offer_instance = Offer.objects.get(start_date__lte = now,end_date__gte=now,is_deleted=False,branch=branch,price_offers__pk=offer_id)
                products= Branch_products.objects.filter(offers__offer = offer_id)
                price_offer_total += offer_instance.price_offers.price * amount
                offer_total = offer_instance.price_offers.price * amount
                for product in products:
                    offer_amount = product.offers.values()[0]['number'] * amount 
                    if product.amount > offer_amount:
                        product.amount -= offer_amount
                        product.save()
                    else :
                        raise ValueError(f'there insufficient amount of the product {product.pk} at gym {product.branch.gym.name} in branch {product.branch.address} while purchasing the offer {offer_instance.name}')
                for offer_ in purchasing_instance.PriceOffers.values():

                    if offer_id == offer_['price_offer_id']:
                        print('heeeeeeeeeeeeeere')
                        try:
                            print(offer_id)
                            price_offer_instance = Purchase_PriceOffer.objects.get(price_offer_id=offer_id,purchase = purchasing_instance.pk,is_deleted=False)
                            flag = True

                            price_offer_instance.amount += amount
                            price_offer_instance.offer_total += offer_total

                            
                            price_offer_instance.save()
                            break
                        except Purchase_PriceOffer.DoesNotExist:
                            print(f'excption was risen {flag}')
                            pass
                        
                if not flag :
                    print('doesnot exist')
                    Purchase_PriceOffer.objects.create(
                            purchase = purchasing_instance,
                            price_offer = offer_instance.price_offers,
                            amount =  amount,
                            offer_total = offer_total,
                            unit_price = offer_instance.price_offers.price
                        )

            except Offer.DoesNotExist or Branch_products.DoesNotExist:
                pass
            print(f'offer price total{price_offer_total}')
            return price_offer_total
        
        
    @staticmethod  
    def use_price_offer(price_offer,purchasing_instance,branch,now):
        price_offer_total = 0
        for offer in price_offer:
            price_offer_total = PrivateStoreService.price_offers_proccessing(offer['offer_id'],now,offer['amount'],branch,purchasing_instance,price_offer_total)
        return price_offer_total 
            
            
     
    @staticmethod 
    def use_percentage_offer(product_type,percentage_offer,branch_product,products_total,product_offered_total):
        if percentage_offer[product_type] is not None:                    
                discount = products_total * (percentage_offer[product_type] / 100)
                product_offered_total = products_total - discount
                
        elif (product_type == 'Supplement'):
                supplement_category_name= Supplements.objects.get(pk=branch_product.product_id).supplement_category.name
            
                if (supplement_category_name in percentage_offer['supplement_category']):
            
                    discount = products_total * (percentage_offer['supplement_category'][supplement_category_name] / 100)
                    product_offered_total = products_total - discount
        return  product_offered_total
    
    @staticmethod
    def use_voucher(vouchers,offered_total):
        discount_amount = offered_total * (vouchers / 100)   
        offered_total -= discount_amount
        return offered_total

        
        
    @staticmethod
    def purchase_management(products,percentage_offer,vouchers,price_offer_total,purchasing_instance):
        total = price_offer_total
        offered_total = price_offer_total
        points_gained = 0 
        for product in products:
            
            products_total = 0
            product_offered_total = 0
            flag = False
            
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
            for item in purchasing_instance.products.values():
                print(product['branch_product_id'])
                if item['product_id'] == product['branch_product_id'].pk:
                    print(f'percentage offer {percentage_offer}')
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
                print('does not exist in previous purchase')
                Purchase_Product.objects.create(
                    purchase = purchasing_instance,
                    product = product['branch_product_id'],
                    amount = product['amount'],
                    product_total = products_total,
                    product_offer_total = product_offered_total,
                    unit_price = branch_product.price,
                    unit_offered_price = product_offered_total / amount
                    
                )
        if vouchers != 0:
            offered_total = PrivateStoreService.use_voucher(vouchers,offered_total)
            
        return {
            'total': total,
            'offered_total': offered_total,
            'points':points_gained,
            }
        
    
    @staticmethod 
    def wallet_cut(total,client):
        
        total = total['offered_total']
        
        wallet = Wallet.objects.get(client=client)
   
        if wallet.balance >= total:
            wallet.balance -= total
            wallet.save()
            
            Wallet_Deposit.objects.create(
                client=client,
                amount = total,
                tranasaction_type = 'cut'
            )
        else :
            raise ValueError({'error':'user does not have enough money'})
        
    @staticmethod
    def Purchase(data):
        products = data.pop('products')
        vouchers_code = data.pop('vouchers',[])
        voucher_discount = 0
        client = data['client']
        now = datetime.now().date()
        price_offer = data.pop('price_offers',[])
        price_offer_total = 0
        branch = data['branch']
        
        purchasing_instance = Purchase.objects.create(
            client=client,
            is_public=False
            
        )
        
        percentage_offer = PrivateStoreService.check_percentage_offers(branch,now)
        if price_offer != []:
            price_offer_total = PrivateStoreService.use_price_offer(price_offer,purchasing_instance,branch,now)
        if vouchers_code != []:
            voucher_discount = PrivateStoreService.check_voucher(client,vouchers_code,now)
        
        total = PrivateStoreService.purchase_management(products, percentage_offer,voucher_discount,price_offer_total,purchasing_instance)
        client.points += total['points']
        client.save()
        
        purchasing_instance.total = total['total']
        purchasing_instance.offered_total = total['offered_total'] if total['offered_total'] != total['total'] else None
        purchasing_instance.save()
        
        PrivateStoreService.wallet_cut(total,client)
        return purchasing_instance
