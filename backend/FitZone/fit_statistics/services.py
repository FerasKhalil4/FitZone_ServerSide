from user.models import User
from gym.models import Gym, Branch
from datetime import datetime
from Vouchers.models import Redeem
from gym_sessions.models import Gym_Subscription, Branch_Sessions
from datetime import datetime, timedelta, timezone
from purchasing.models import Purchase_Product, Purchase_PriceOffer
from store.models import Supplements, Accessories, Meals
from store.serializers import SupplementsSerializer, MealsSerializer, AccessoriesSerializer
from classes.models import Classes, Class_Scheduel ,Client_Class

def get_duration_in_foramts(month=None, year=None) -> tuple:
    now = datetime.now().date()
    month = now.month if month is None else month
    year = now.year if year is None else year
    return now, month, year


class AdminStatsService():
    
    @staticmethod
    def get_user_stats(month=None,year=None) -> dict:
        now, _, year = get_duration_in_foramts(month,year)
        current_month_users = User.objects.filter(date_joined__month = now.month ,is_deleted = False).count()
        users_spec_month = User.objects.filter(date_joined__month=month,date_joined__year = year,is_deleted=False).count()
        
        users_across_year = User.objects.filter(is_deleted=False,date_joined__year = year)
        users = {}
        for user in users_across_year:
            if user.date_joined.month not in users:
                users[user.date_joined.month] = 1
            else:
                users[user.date_joined.month] += 1
        
        return {
            'users_across_year':users,
            'current_month_users': current_month_users,
            'users_specific_month': users_spec_month,
        }
        
    @staticmethod
    def get_gym_stats() -> dict:
        gyms = Gym.objects.filter(is_deleted=False).count()
        branches = Branch.objects.filter(gym__is_deleted=False)     
        
        branches_count = {}
        
        for branch in branches:
            if branch.gym.pk not in branches_count:
                branches_count[branch.gym.pk] = {}
                branches_count[branch.gym.pk]['branch_count'] = 1
                branches_count[branch.gym.pk]['avg_branches_rating'] = branch.rate
                branches_count[branch.gym.pk]['num_ratings'] = branch.number_of_rates
            else:
                branches_count[branch.gym.pk]['branch_count'] += 1
                branches_count[branch.gym.pk]['avg_branches_rating'] += branch.rate
                branches_count[branch.gym.pk]['num_ratings'] += branch.number_of_rates
        
        for branch in branches_count:
            branches_count[branch]['avg_branches_rating'] = branches_count[branch]['avg_branches_rating'] / branches_count[branch]['branch_count'] 
        
        return {
            'gyms_count':gyms,
            'gyms_data' : branches_count
        }
            
    @staticmethod
    def get_vouchers_data(month=None, year=None) -> dict:
        
        _, month, year = get_duration_in_foramts(month,year)
        
        
        vouchers_across_year = Redeem.objects.filter(start_date__year = year)
        
        vouchers = {}
        for voucher in vouchers_across_year:
                if voucher.start_date.month not in vouchers:
                    vouchers[voucher.start_date.month] = {}
                    vouchers[voucher.start_date.month]['count'] = 1
                    vouchers[voucher.start_date.month]['voucher_name'] = voucher.voucher.name
                else:
                    vouchers[voucher.start_date.month]['count'] += 1
                    
        vouchers_in_month = Redeem.objects.filter(start_date__month = month).count()
        
        return {
            'vouchers_in_month':vouchers_in_month,
            'vouchers_across_year':vouchers
        }

class ManagerStatsService():
    
    @staticmethod
    def get_branches_stats(manager,year=None)->dict:
        
        _, _, year = get_duration_in_foramts(year)
        
        
        branches = Branch.objects.filter(gym__manager = manager, gym__is_deleted = False)
        branches_details ={}
        
        for branch in branches:
            
            if branch.gym.name not in branches_details:
                branches_details[branch.gym.name] = []
                
            branches_details[branch.gym.name].append({
                'branch_pk' : branch.pk,
                'address' : f'{branch.city} - {branch.street} - {branch.address}',
                'current_number_of_clients' : branch.current_number_of_clients,
                'rate' : branch.rate,
                'number_of_ratings' : branch.number_of_rates,
                'activity_status':branch.is_active
            })
            
            active_subscriptions = Gym_Subscription.objects.filter(start_date__year = year,is_active = True, branch=branch.pk)
        
            sub_data = {}
            for subscription in active_subscriptions:
                
                if subscription.start_date.month not in sub_data:
                    sub_data[subscription.start_date.month] = {}
                    sub_data[subscription.start_date.month][subscription.registration_type.type] = {}
                    
                    sub_data[subscription.start_date.month][subscription.registration_type.type]['count'] = 1
                    sub_data[subscription.start_date.month][subscription.registration_type.type]['fee'] = subscription.registration_type.fee
                    
                else:
                    if subscription.registration_type.type not in sub_data[subscription.start_date.month]:
                        sub_data[subscription.start_date.month][subscription.registration_type.type] = {}
                        
                        sub_data[subscription.start_date.month][subscription.registration_type.type]['count'] = 1
                        sub_data[subscription.start_date.month][subscription.registration_type.type]['fee'] = subscription.registration_type.fee
                        
                    else:
                        sub_data[subscription.start_date.month][subscription.registration_type.type]['count'] += 1
                    

        return {
            'subscriptions_data':sub_data,
            'branches_details':branches_details
        }
        
    @staticmethod
    def get_branch_sessions_statistics(gym_manager,year,month) -> dict:
        
        current_date =  datetime.now(timezone(timedelta(hours=0)))
        sessions_year = current_date.year if year is None else year
        sessions_month = current_date.month if month is None else month
        
        manager_branches = Branch.objects.filter(gym__manager = gym_manager, gym__is_deleted = False,is_active = True)
        
        
        branches_sessions_details = {}
        for branch in manager_branches:
            branch_sessions_qs = Branch_Sessions.objects.filter(branch = branch,created_at__year=sessions_year,
                                                             created_at__month = sessions_month).distinct('client','created_at__year',
                                                                                                            'created_at__month', 'created_at__day',
                                                                                                            'created_at__hour')
            
            for session in branch_sessions_qs :
                session_hours = list(range(session.created_at.hour, session.end_session.hour + 1))
                
                for session_duration_in_hours in session_hours :
                    if session.branch.pk not in branches_sessions_details:
                        
                        branches_sessions_details[session.branch.pk] = {}
                        
                        branches_sessions_details[session.branch.pk]['address' ] = f'{session.branch.city} - {session.branch.street} - {session.branch.address}'
                        branches_sessions_details[session.branch.pk]['gym' ] = session.branch.gym.name  
                        branches_sessions_details[session.branch.pk][session_duration_in_hours] = 1
                        
                    else:
                        if session_duration_in_hours not in branches_sessions_details[session.branch.pk]:
                            branches_sessions_details[session.branch.pk][session_duration_in_hours] = 1
                            
                        else:
                            branches_sessions_details[session.branch.pk][session_duration_in_hours] += 1
        
        return {
            'branches_sessions_details':branches_sessions_details
        }
        

        
    @staticmethod 
    def get_month_data_struct(product_data,product_item,purchased_product,serialized_data) -> dict:
        
        product_data[f'{purchased_product.purchase.created_at.month}_month'][product_item.pk] = {}
        product_data[f'{purchased_product.purchase.created_at.month}_month'][product_item.pk]['details'] = serialized_data
        product_data[f'{purchased_product.purchase.created_at.month}_month'][product_item.pk]['purchased_amount'] = purchased_product.amount
        return product_data
        
    @staticmethod
    def get_products_details(qs) -> dict:
        
        product_data = {}
        for purchased_product in qs:
            product_item = purchased_product.product
            
            if product_item.product_type == 'Supplement':
                product = Supplements.objects.get(pk=product_item.product_id)
                serialized_data = SupplementsSerializer(product).data
                
            elif product_item.product_type == 'Meal':
                product = Meals.objects.get(pk=product_item.product_id)
                serialized_data = MealsSerializer(product).data
                

            elif product_item.product_type == 'Accessory':
                product = Accessories.objects.get(pk=product_item.product_id)
                serialized_data = AccessoriesSerializer(product).data
                
            serialized_data['product'].pop('image_path')
            serialized_data['price'] = product_item.price
            serialized_data['amount'] = product_item.amount
            
            if f'{purchased_product.purchase.created_at.month}_month' not in product_data:
                product_data[f'{purchased_product.purchase.created_at.month}_month']= {}
                product_data = ManagerStatsService.get_month_data_struct(product_data,product_item,purchased_product,serialized_data)
            
            else:
                if product_item.pk not in product_data[f'{purchased_product.purchase.created_at.month}_month']:
                    product_data = ManagerStatsService.get_month_data_struct(product_data,product_item,purchased_product,serialized_data)

                else:
                    product_data[f'{purchased_product.purchase.created_at.month}_month'][product_item.pk]['purchased_amount'] += purchased_product.amount
                
        return product_data
    
    
    @staticmethod
    def get_offer_struct(offer_details,offer_item,purchased_offer) -> dict:
        
        offer_month_details = offer_details[f'{purchased_offer.purchase.created_at.month}_month']
        offer_month_details[offer_item.pk] = {}
        
        offer_month_details[offer_item.pk]['name'] = offer_item.offer.name
        offer_month_details[offer_item.pk]['price'] = offer_item.price
        offer_month_details[offer_item.pk]['details'] = f'from {offer_item.offer.start_date} to {offer_item.offer.end_date}'
        offer_month_details[offer_item.pk]['purchased_amount'] = purchased_offer.amount
        
        return offer_details
    
    @staticmethod
    def get_offer_details(qs) -> dict:
        offer_details = {}
        for purchased_offer in qs:
            offer_item = purchased_offer.price_offer
            if f'{purchased_offer.purchase.created_at.month}_month' not in offer_details:
                offer_details[f'{purchased_offer.purchase.created_at.month}_month'] = {}
                offer_details = ManagerStatsService.get_offer_struct(offer_details,offer_item,purchased_offer)
            
            else:
                if offer_item.pk not in offer_details[f'{purchased_offer.purchase.created_at.month}_month']:
                    offer_details = ManagerStatsService.get_offer_struct(offer_details,offer_item,purchased_offer)
                else:
                    offer_details[f'{purchased_offer.purchase.created_at.month}_month'][offer_item.pk]['purchased_amount'] += purchased_offer.amount
        
        return offer_details
    @staticmethod
    def get_products_sattistics(gym_manager,year) -> dict:
        
        _, _, year = get_duration_in_foramts(year)
        
        manager_branches = Branch.objects.filter(gym__manager = gym_manager, gym__is_deleted = False,is_active = True)
        products_details = {}
        offer_details = {}
        for branch in manager_branches:
            
            products_details[branch.pk] = {}
            products_details[branch.pk]['address'] = f'{branch.city} - {branch.street} - {branch.address}'
            products_details[branch.pk]['gym'] = branch.gym.name
            products_details[branch.pk]['products'] = {}
            
            products_purchased_qs = Purchase_Product.objects.filter(product__branch = branch,purchase__created_at__year = year,is_deleted = False, purchase__is_deleted = False)
            products_details[branch.pk]['products'] = ManagerStatsService.get_products_details(products_purchased_qs)
            
            price_offers_purchased_qs = Purchase_PriceOffer.objects.filter(price_offer__offer__branch = branch,purchase__created_at__year = year)
            offer_details[branch.pk] = {}
            offer_details[branch.pk]['address'] = f'{branch.city} - {branch.street} - {branch.address}'
            offer_details[branch.pk]['gym'] = branch.gym.name
            offer_details[branch.pk]['offers'] = {}
            offer_details[branch.pk]['offers'] = ManagerStatsService.get_offer_details(price_offers_purchased_qs)
            
        return {
                'products_details':products_details,
                'offer_details':offer_details
            }
                        
                        
    @staticmethod
    def get_classes_dict_struct(class_details, branch, active_class):
        
            class_details[branch.pk]['classes'][active_class.class_id.class_id.pk] = {}
            class_data = class_details[branch.pk]['classes'][active_class.class_id.class_id.pk]
            class_data['date'] = f'from {active_class.class_id.start_date} to {active_class.class_id.end_date}'
            class_data['time'] = f'from {active_class.class_id.start_time} to {active_class.class_id.end_time}'
            class_data['days_of_week'] = '-'.join(list(active_class.class_id.days_of_week.values()))
            class_data['name'] = active_class.class_id.class_id.name
            class_data['hall'] = active_class.class_id.hall
            class_data['instructor'] = active_class.class_id.trainer.employee.user.username
            class_data['price'] = active_class.class_id.class_id.registration_fee
            class_data['count'] = 1
            
            return class_details
        
    @staticmethod
    def get_classes_statistics(gym_manager):
        
        manager_branches = Branch.objects.filter(gym__manager = gym_manager, gym__is_deleted = False,is_active = True)
        class_details = {}
        
        
        for branch in manager_branches:
            active_classes = Client_Class.objects.filter(class_id__class_id__branch = branch, class_id__is_deleted = False, class_id__class_id__is_deleted = False,is_deleted = False)
            
            for active_class in active_classes:
                if branch.pk not in class_details:
                    
                    class_details[branch.pk] = {}
                    class_details[branch.pk]['address'] = f'{branch.city} - {branch.street} - {branch.address}'
                    class_details[branch.pk]['gym'] = branch.gym.name
                    class_details[branch.pk]['classes'] = {}
                    
                    class_details = ManagerStatsService.get_classes_dict_struct(class_details, branch, active_class)
                
                else:
                    if active_class.class_id.class_id.pk not in class_details[branch.pk]['classes']:
                        class_details = ManagerStatsService.get_classes_dict_struct(class_details, branch, active_class)
                        
                    else:
                        class_details[branch.pk]['classes'][active_class.class_id.class_id.pk]['count'] += 1
                    
        return class_details
        