from ..models import *
from datetime import datetime 
from dateutil.relativedelta import relativedelta
from .private_store_service import PrivateStoreService
from datetime import datetime
from django.db import transaction
from wallet.models import Wallet,Wallet_Deposit
from .public_store_services import *
from .private_store_service import *
from gym.models import Branch

class UpdatePurchasing():
    
    @staticmethod
    def delete_product(product_total,gym_percentage_cut,new_total):
        # print('product will be deleted')
        # print(f'previous total {new_total}')
        # print(f'prioduct total {product_total}')
        # print(f'gym percentage cut  {gym_percentage_cut}')
        
        discount = product_total * gym_percentage_cut
        # print(f'discount {discount}')
        total_retrieved = discount - product_total
        # print(f'retived value {total_retrieved}')
        new_total += total_retrieved
        print(f'delete item new total {new_total}')
        
        # print(f'new total {new_total}')
        return {'new_total':new_total,'item_total':total_retrieved}
    
    @staticmethod
    def update_product_amount(product_purchased,percentage_offers,product_type,single_product_price,gym_percentage_cut,new_total,amount):
        product_purchased.amount += amount
        product_purchased.save()
        client_total = True
        product_totel_price = 0
        print(new_total)
        
        print("##########################################################33")
        # print(amount)
        if amount > 0 :
            # print('amount greater than previous amount')
            product_totel_price = product_purchased.product.price * amount
            # print(product_purchased.product.price)
            
            # print(f'base product total price {product_totel_price}')
            
            if percentage_offers[product_type] is not None:
                # print('percentage offer activated')
                discount = product_totel_price * (percentage_offers[product_type] / 100)
                # print(f'discount {discount}')
                product_totel_price -= discount
                # print(f'discounted product total price {product_totel_price}')
        elif amount < 0:
            # print('amount less than previous amount')
            # print(f'previous total amount{new_total}')
            # print(f'single prodct price{single_product_price}')
            # print(f'amount{amount}')
            # print(f'gym percentage cut  {gym_percentage_cut}')
            
    

            
            # print(f'product total price {product_totel_price}')
            # print('######################')
            # print(amount)
            # print(single_product_price)
            # print(product_totel_price)
            # print(gym_percentage_cut)
            if gym_percentage_cut != 1 and gym_percentage_cut != 0 :
                print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSsss")
                print(product_totel_price)
                print(gym_percentage_cut)
                product_totel_price = single_product_price * amount * gym_percentage_cut 
                # print(f'discount {discount}')
                print(product_totel_price)
            elif gym_percentage_cut == 1:
                print('##############################################################################################')
                product_totel_price = 0
                client_total = False
            elif gym_percentage_cut == 0:
                product_totel_price = single_product_price * amount
        else:
            client_total = False
                
        item_total = single_product_price * amount
        print(item_total)
        print(product_purchased.product_total)
        print(product_purchased.product_offer_total)
        print('JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ')
        new_total += product_totel_price
        
        # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        # print(item_total)
        product_purchased.save()
        print(f'new total {new_total}')
        return {'new_total': new_total, 'item_total': item_total,'client_total': client_total}
    
    @staticmethod
    def update_products(products,now,new_total):
        new_points = 0
        base_total = 0
        client_total = 0
        flag = True

        for product in products:

            product_purchased = product['purchase_product_id']                
            product_total = product_purchased.product_offer_total if (product_purchased.product_offer_total < product_purchased.product_total) and(product_purchased.product_offer_total)  != 0 else product_purchased.product_total
            percentage_offers = PrivateStoreService.check_percentage_offers(product_purchased.product.branch.pk,now)
            product_type = product_purchased.product.product_type
            single_product_price = product_total / product_purchased.amount
            print(single_product_price)
            print('111111111')
            branch_product = Branch_products.objects.get(pk=product_purchased.product.pk)
            if product_purchased.product.branch.gym.cut_percentage is not None:
                gym_percentage_cut = 100 - product_purchased.product.branch.gym.cut_percentage 
                gym_percentage_cut = (gym_percentage_cut / 100) 
            else:
                gym_percentage_cut = 1
            print(gym_percentage_cut)
            print('?????????????????????????????????/')

            # print('==================================')
            # print(product)
            # print(product['purchase_product_id'].product.price)
            # print(gym_percentage_cut)
            # print('==================================')
            if 'amount' in product or product['amount'] is None:
                print('==================================')
                amount = product['amount'] - product_purchased.amount
                print(amount)
                print('==================================')
                branch_product.amount += (-amount)
                new_points += branch_product.points_gained * amount
                
                update_product = UpdatePurchasing.update_product_amount(product_purchased,percentage_offers,product_type,single_product_price,gym_percentage_cut,new_total,amount)
                new_total = update_product['new_total']
                item_total = update_product['item_total']
                print(update_product['client_total'])
                print("AWWWWWWWWWQQQQQQQQQQQQQQQQQQQFFFFFFFFFFFFFFFFFf")
                flag = update_product['client_total']
                if flag:
                    client_total += new_total 
                    print(client_total)
                    
                if product_purchased.product_offer_total < product_purchased.product_total and product_purchased.product_offer_total != 0 :
                    print(item_total)
                    print(')))))))))))))))))))))))')
                    print(product_purchased.product_offer_total)
                    print(product_purchased.product_total)
                    print(item_total)
                    print(branch_product.price * amount)
                    print('before')
                    product_purchased.product_offer_total += item_total
                    product_purchased.product_total += branch_product.price * amount
                    print(product_purchased.product_offer_total)
                    print(product_purchased.product_total)
                    print('after')
                    print(')))))))))))))))))))))))')
                    
                else:
                    product_purchased.product_total += item_total
                product_purchased.save()
                # print(f' new item totel is {item_total}')


            elif 'is_deleted' in product or product['is_deleted'] is None: 
                amount = -product_purchased.amount
                branch_product.amount += product_purchased.amount
                new_points -= branch_product.points_gained * product_purchased.amount
                product_purchased.is_deleted = True
                product_purchased.save()
                
                delete_item = UpdatePurchasing.delete_product(product_total,gym_percentage_cut,new_total)
                print(delete_item['new_total'])
                print(f'delete product {client_total}')
                
                client_total += delete_item['new_total'] if flag is True else client_total
                print(f'delete product {client_total}')
                
                print(client_total)
                print("QQQQQQNKKKKKKKKKKKKKKK")
                
                new_total =delete_item['new_total'] if flag is True else new_total
                item_total = delete_item['item_total']
                
                # print(f' new item totel is {item_total}')
            print('3333333333333333333333333333333333333333333333333333')

            print(client_total)
            print('3333333333333333333333333333333333333333333333333333')
            
            # print(f'old price offer total {product_purchased.product_total}')
            if flag:
                if amount < 0:
                    if gym_percentage_cut != 1 and gym_percentage_cut != 0:
                        base_total += branch_product.price * amount * gym_percentage_cut
                    elif gym_percentage_cut == 1 :
                        base_total += 0
                    elif gym_percentage_cut == 0 :
                        base_total += branch_product.price * amount 
                if amount > 0 :
                    base_total += branch_product.price * amount
                    
            print(branch_product.price * amount)
            print(amount)
            print('"""""""""""""""""""""""""""""""""""""')
            
            print(base_total)
            print('"""""""""""""""""""""""""""""""""""""')
            

            
            # print(f'new price offer total {product_purchased.product_total}')
            branch_product.save()
        print(client_total)
        return {'new_total':new_total,'new_points':new_points,'base_total':base_total,'client_total':client_total}
    
    
    @staticmethod
    def update_price_offer_product_amount(products,amount):
        # print('OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
        for product in products:
            # print(product)
            product_instance = Branch_products.objects.get(pk = product['product_id'])
            # print(f'previous product amount {product_instance.amount}')
            # print(amount)
            # print(product['number'])
            product_instance.amount += ((-amount) * product['number'])
            product_instance.save()
            # print(f'new product amount {product_instance.amount}')
            
    
    @staticmethod
    def delete_price_offer(price_offer_purchased,gym_percentage_cut,new_total,amount):
        new_total = UpdatePurchasing.delete_product(price_offer_purchased.offer_total,gym_percentage_cut,new_total)
        price_offer_purchased.is_deleted = True 
        products = price_offer_purchased.price_offer.objects.values()
        UpdatePurchasing.update_price_offer_product_amount(products,amount)
        
        return new_total
        
    @staticmethod
    def update_offer_products(price_offer_purchased,new_total,gym_percentage_cut,amount):
        print(f'gym percentage cut {gym_percentage_cut}')
        client_total = True

        products = price_offer_purchased.price_offer.objects.values()
        # print(products)

        offer_totel_price = price_offer_purchased.price_offer.price * amount

        # print(f'base total price {offer_totel_price}')
        
        # if amount > 0 : 
        #     print('amounts greater than 0')
        #     print(f'price offer instance {price_offer_purchased}')
        #     print(f'offer products {products}')
        #     print(f'current total {new_total}')
        #     print(f'price_offer total {price_offer_purchased.offer_total}')
        #     print(f'new total {new_total + price_offer_purchased.offer_total }')
        #     print(f'amount{amount}')
            
            
            
        if amount < 0:
            # print('amounts less than 0') 
            # print(f'price offer instance {price_offer_purchased}')
            # print(f'offer products {products}')
            # print(f'current total {new_total}')
            # print(f'price_offer total {price_offer_purchased.offer_total}')
            # print(f'discount gym percentage cut {price_offer_purchased.offer_total * gym_percentage_cut}')
            # print(f'amount{amount}')
            if gym_percentage_cut != 1 and gym_percentage_cut != 0 :
                offer_totel_price = offer_totel_price * gym_percentage_cut
                # print(f'discount {discount}')
                print(offer_totel_price)
                print(f'offer total price {offer_totel_price}')
            elif gym_percentage_cut == 1:
                client_total = False
                offer_totel_price = 0
            elif gym_percentage_cut == 0:
                offer_totel_price = price_offer_purchased.price_offer.price * amount
                
        elif amount == 0 :
            client_total = False
            
            
        UpdatePurchasing.update_price_offer_product_amount(products,amount)
        print(f'here{new_total}')
        print(offer_totel_price)
        new_total += offer_totel_price
        price_offer_purchased.amount += amount
        
        item_total = offer_totel_price

        print(new_total)
        # print(f'item total {item_total}')
        
        return {'new_total': new_total,'item_total': item_total,'client_total': client_total}
    @staticmethod
    def update_offers(offers,new_total):
        # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        client_total = 0
        flag = True
        for offer in offers:
            # print(offer)
            price_offer_purchased = offer['purchase_price_offer_id']
            base_total = 0
            if price_offer_purchased.price_offer.offer.branch.gym.cut_percentage is not None:
                gym_percentage_cut = 100 - price_offer_purchased.price_offer.offer.branch.gym.cut_percentage
                gym_percentage_cut = (gym_percentage_cut / 100) 
            else:
                gym_percentage_cut = 1
            if not price_offer_purchased.price_offer.offer.is_deleted:
                if 'amount' in offer or offer['amount'] is not None:
                    amount = offer['amount'] - price_offer_purchased.amount
                    # print('=======================')
                    
                    # print(new_total)
                    update_product =  UpdatePurchasing.update_offer_products(price_offer_purchased,new_total,gym_percentage_cut,amount)
                    new_total = update_product['new_total']
                    
                    item_total = update_product['item_total']
                    flag = update_product['client_total']
                    if flag:
                        client_total += new_total 
                        print(f'current client total in offers{client_total}')
                    print(new_total)
                    print("AWJ MMMMMMMMMMMMMMMMMMMMm")
                    price_offer_purchased.offer_total += item_total
                    price_offer_purchased.amount += amount
                    price_offer_purchased.save()
                    
                    # print(new_total)
                    
                    # print('=======================')
                elif 'is_deleted' in offer or offer['is_deleted'] is not None: 
                    amount = -price_offer_purchased.amount
                    delete_item = UpdatePurchasing.delete_price_offer(price_offer_purchased,gym_percentage_cut,new_total,amount)
                    new_total = delete_item['new_total'] if flag is True else  new_total 
                    print(f'delete offer {client_total}')
                    client_total = delete_item['new_total'] if flag is True else client_total
                    print(f'delete offer {client_total}')
                    
                    item_total = delete_item['item_total']
                    
                if flag :
                    if amount < 0 :
                        if gym_percentage_cut != 1 and gym_percentage_cut != 0:
                            base_total += price_offer_purchased.price_offer.price * amount * gym_percentage_cut 
                        elif gym_percentage_cut == 1 :
                            base_total += 0 
                        elif gym_percentage_cut == 0 :
                            base_total += price_offer_purchased.price_offer.price * amount 
                    if amount > 0:
                        base_total += price_offer_purchased.price_offer.price * amount
            # print(f'new item totel is {item_total}')
            # print(f'old price offer total{price_offer_purchased.offer_total}')

                
                # print(f'base total{base_total}')
                
                # print(f'new price offer total{price_offer_purchased.offer_total}')
                
                # print('@@@@@@@@@@@@@@@@@@@@@@@@')
                
                # print(f'new total{new_total}')
                
                # print('@@@@@@@@@@@@@@@@@@@@@@@@')
                

                
                # print(f'new price offer total{price_offer_purchased.offer_total}')
                
                # print('@@@@@@@@@@@@@@@@@@@@@@@@')
                
                # print(f'new total{new_total}')
                
                # print('@@@@@@@@@@@@@@@@@@@@@@@@')
                
                # print(f'new item totel is {item_total
            # print(f'new price offer total{price_offer_purchased.offer_total}')
            price_offer_purchased.save()
            
        return {'new_total':new_total,'base_total':base_total,'client_total':client_total}
    
    @staticmethod
    def update_purchasing_instance(instance,data):
        try:
            with transaction.atomic():
        
                client = Client.objects.get(pk=instance.client.pk)
                products = data.pop('products_updated',[])
                offers = data.pop('offers_updated',[])
                now = datetime.now().date()
                product_new_total = 0
                new_total = 0 
                base_total = 0
                client_total = 0
                if products != []:
                    product_new_total = UpdatePurchasing.update_products(products,now,new_total)
                    new_total += product_new_total['new_total']
                    base_total += product_new_total['base_total']
                    print('AAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    
                    client_total += product_new_total['client_total']
                    print('AAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    
                    print(product_new_total)
                    print(f'client total {client_total}')
                    client.points += product_new_total['new_points']
                    client.save()
                print("AQQQQQQQQQQQQQQQQQQQQQQQQQQQQE")
                        
                    # print(new_total)
                if offers != []:
                    print(offers)
                    offers_new_total = UpdatePurchasing.update_offers(offers,new_total)
                    
                    new_total = offers_new_total['new_total'] 
                    base_total += offers_new_total['base_total']
                    print("QQQQQQQQQQQQQQEEEEEEEEEEERR")
                    print(offers_new_total)
                    print(client_total)
                    print(offers_new_total['client_total'])
                    client_total = offers_new_total['client_total']
                    print(client_total)
                    print("QQQQQQQQQQQQQQEEEEEEEEEEERR")
                    
                # print(new_total)
                # print('@@@@@@@@@@@@@@@@@@@@@@@@')

                wallet = Wallet.objects.get(client=client.pk)
                
                print(f'wallet old balance {wallet.balance}')
                if (client_total > wallet.balance) and (client_total > 0): 
                    raise ValueError('insufficient amount of money in the clients wallet')
                wallet.balance -= client_total
                print(f'wallet new balance {wallet.balance}')
                # print('-------------------------------------------')
                
                wallet.save()
                if new_total != 0:
                    if new_total < 0:
                        tranasaction_type = 'retrieve'
                    elif new_total > 0:
                        tranasaction_type = 'cut'
                    print(tranasaction_type)
                    
                    Wallet_Deposit.objects.create(
                        client=client,
                        amount = abs(client_total),
                        tranasaction_type = tranasaction_type
                    )

                print(f'last total amount {new_total}')
                print(f'old offer total amount {instance.offered_total}')
                print(f'old total amount {instance.total}')
                
                print(new_total)
                if instance.offered_total < instance.total and instance.offered_total != 0 :
                    instance.offered_total += new_total
                    instance.total += base_total
                else:
                    instance.total += new_total
                print(f'new offer total amount {instance.offered_total}')
                print(f'new total amount {instance.total}')
                
                instance.number_of_updates += 1
                instance.save()
                # '0'-0

                # print('___________________________________')
            return instance
                
        except Exception as e:
            raise ValueError (str(e))

class Check_Update():
    @staticmethod
    def check_products(product_gym,gym,item,created_at) -> None:
        now = datetime.now().date()
        if product_gym.allow_retrival:
            if product_gym.pk not in gym :
                allowed_date = created_at.date() + relativedelta(days=product_gym.duration_allowed)
                if  now <= allowed_date:
                    
                    item['allow_update'] = True
                    gym[product_gym.pk] = True
                
                else:
                    # excluded_id = item.pk
                    item['allow_update'] = False
                    gym[product_gym.pk] = False
            else:
                item['allow_update'] = gym[product_gym.pk]
                    
        else: 
            # excluded_id = item.pk
            item['allow_update'] = False
            gym[product_gym.pk] = False
            

    @staticmethod
    def check_editings(data):
        gym = {}
        
        purchases = data['products']
        offers = data['PriceOffers']
        purchase_instance = Purchase.objects.get(pk=data['purchase_pk'])
        
        for purchase in purchases:
            product_gym = Branch.objects.get(pk=purchase['product_details']['branch']['id']).gym

            if (purchase_instance.number_of_updates <= product_gym.allowed_number_for_update) :
                Check_Update.check_products(product_gym,gym,purchase,purchase_instance.created_at)
                print(Check_Update.check_products(product_gym,gym,purchase,purchase_instance.created_at))
                
            else:
                purchase['allow_update'] = False
            
        for offer in offers:
            product_gym = Branch.objects.get(pk=offer['offer_detail']['branch']['id']).gym
            
            if (purchase_instance.number_of_updates <= product_gym.allowed_number_for_update) :
                Check_Update.check_products(product_gym,gym,offer,purchase_instance.created_at)
                print(Check_Update.check_products(product_gym,gym,offer,purchase_instance.created_at))
                
            else:
                offer['allow_update'] = False

        return data

class AddProductToPurchase():
    
    @staticmethod
    def add_product(data):
        try:
            products = data.pop('products')
            vouchers_code = data.pop('vouchers',[])
            voucher_discount = 0
            purchasing_instance = data.pop('id')
            client = purchasing_instance.client
            now = datetime.now().date()
            price_offer = data.pop('price_offers',[])
            price_offer_total = 0
            number_of_updates = data.pop('number_of_updates')
            purchase_instance_products= purchasing_instance.products.values()
            purchase_instance_offers = purchasing_instance.PriceOffers.values()
            branch = data.pop('branch_id',None)
            
            print(purchase_instance_products)
            print(purchase_instance_offers)
            if price_offer != []:
                if branch is not None:
                    price_offer_total = PrivateStoreService.use_price_offer(price_offer,purchasing_instance,branch,now)
                else:
                    price_offer_total = PublicPurchaseService.use_price_offer(price_offer,purchasing_instance,now)
            print(price_offer_total)
            print('in update')
                
            if vouchers_code != []:
                voucher_discount = PrivateStoreService.check_voucher(client,vouchers_code,now)

            if branch is not None:
                percentage_offer = PrivateStoreService.check_percentage_offers(branch,now)
                total = PrivateStoreService.purchase_management(products, percentage_offer,voucher_discount,price_offer_total,purchasing_instance)
            else:
                total = PublicPurchaseService.purchase_management(products,voucher_discount,price_offer_total,purchasing_instance)

            client.points += total['points']
            client.save()
            print(total)
            purchasing_instance.total += total['total']
            purchasing_instance.offered_total += total['offered_total'] if 0 < total['offered_total'] < total['total'] else None
            purchasing_instance.save()
            PrivateStoreService.wallet_cut(total,client)
            
            if number_of_updates is None :
                print(purchasing_instance.number_of_updates )
                purchasing_instance.number_of_updates += 1  
                print(purchasing_instance.number_of_updates )
                purchasing_instance.save()
            return purchasing_instance
        except Exception as e:
            raise ValueError(str(e))
        
        
        
    #         @staticmethod
    # def check_editings(pk):
    #     gym = {}
    #     excluded_ids = []
        
    #     purchases = Purchase_Product.objects.filter(purchase=pk,is_deleted=False)
    #     offers = Purchase_PriceOffer.objects.filter(purchase=pk,is_deleted=False)
    #     purchase_instance = Purchase.objects.get(pk=pk)
    #     for purchase in purchases:
    #         product_gym = purchase.product.branch.gym

    #         if (purchase_instance.number_of_updates <= product_gym.allowed_number_for_update) :
    #             excluded_id = Check_Update.check_products(product_gym,gym,purchase)
    #             if excluded_id is not None:
    #                 excluded_ids.append(excluded_id) 
    #         else:
    #             excluded_ids.append(purchase.pk) 
                
    #     new_purchases =  purchases.exclude(id__in=excluded_ids)
            
    #     excluded_ids = []
    #     for offer in offers:
    #         product_gym = offer.price_offer.offer.branch.gym
    #         if (purchase_instance.number_of_updates <= product_gym.allowed_number_for_update) :
            
    #             excluded_id = Check_Update.check_products(product_gym,gym,offer)
    #             if excluded_id is not None:
    #                 excluded_ids.append(excluded_id) 
    #         else:
    #             excluded_ids.append(offer.pk) 
                
    #     new_offers = offers.exclude(pk__in=excluded_ids)

    #     return {
    #         'purchases': new_purchases,
    #         'offers':new_offers
    #     } if len(new_purchases) + len(new_offers) > 0 else None