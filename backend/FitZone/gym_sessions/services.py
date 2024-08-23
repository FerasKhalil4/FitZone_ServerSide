from offers.models import ObjectHasPriceOffer,Percentage_offer 
from gym.models import Registration_Fee
from wallet.models import Wallet, Wallet_Deposit
from Vouchers.models import Redeem
from plans.models import Gym_plans_Clients,Gym_Training_plans
from datetime import datetime
from django.core.exceptions import ValidationError
import math

now = datetime.now().date()

class OfferSubscriptionService:
    
    @staticmethod
    def check_price_offers(registration_type,branch):
        try:
            price_offer_check = ObjectHasPriceOffer.objects.get(fee=registration_type,offer__offer__start_date__lte = now,
                                        offer__offer__end_date__gte = now,
                                        offer__offer__is_deleted = False,
                                        offer__offer__branch = branch,
                                        )
            return price_offer_check.offer.price
        except ObjectHasPriceOffer.DoesNotExist:
            return None
        
    def check_percentage_offers(registration_type,code,branch):
        try:
            percentage_offer_check = Percentage_offer.objects.get( fee=registration_type,
                                                                    offer__start_date__lte = now,
                                                                    offer__end_date__gte = now,
                                                                    offer__is_deleted = False,
                                                                    offer__branch = branch.pk
                                                                    ,code=code) 
            
            return percentage_offer_check.percentage_cut
        except Percentage_offer.DoesNotExist:
            return None
    
    def check_vouchers(vouchers,client):
        discount = 0
        for voucher in vouchers:
            try:
                check = Redeem.objects.get(client=client,code=voucher,start_date__lte = now, expired_date__gte = now).voucher.discount
                discount += check
            except Redeem.DoesNotExist:
                pass

        return discount
        
    @staticmethod
    def offer_check(data):
        offer_code = data.pop('offer_code', None)
        vouchers = data.pop('vouchers',None)
        new_fee = None
        
        fee = Registration_Fee.objects.get(pk=data['registration_type'].pk).fee
        
        new_price = OfferSubscriptionService.check_price_offers(data['registration_type'].pk,data['branch'])
        
        if new_price is not None:
                new_fee = new_price
                
        new_fee = new_fee if new_fee is not None else fee
        
        if offer_code is not None:
            
            offer_percentage = OfferSubscriptionService.check_percentage_offers(data['registration_type'], offer_code,data['branch'])
            if offer_percentage is not None:
                discount = new_fee * (offer_percentage / 100)
                new_fee = new_fee - discount

        
        if len(vouchers) != 0 :
            discount_amount = OfferSubscriptionService.check_vouchers(vouchers,data['client'])
            discount = new_fee * (discount_amount / 100) 
            new_fee = new_fee - discount
            
            
        data['price_offer'] = new_fee if new_fee is not None else None   
        return data
    

class SubscriptionService:
    
    @staticmethod 
    def client_points(client,points,flag=None):
        
        if flag :
            
            client.points -= points
            client.save()

        elif flag is None:
            client.points += points
            client.save()
        
            
    @staticmethod
    def check_client_balance(client, fee ,type_):
        
        wallet = Wallet.objects.get(client=client)
        
        if type_ == 'cut':
            print('cut money from clients balance')
            if wallet.balance < fee:
                raise ValidationError('client balance does not have the expected amount')
            else:
                wallet.balance -= fee
                wallet.save()

                Wallet_Deposit.objects.create(client=client
                                                  ,amount=fee
                                                  ,employee=None
                                                  ,tranasaction_type='cut')
                
        elif type_ == 'add':
            
            wallet.balance += fee
            wallet.save()
            
            Wallet_Deposit.objects.create(client=client
                                                ,amount=fee
                                                ,employee=None
                                                ,tranasaction_type='retrieve')
    
class Activate_Gym_Training_PlanService:
    
    @staticmethod
    def add_training_plan(data):
        try:
            check_plan = Gym_Training_plans.objects.get(gym=data['branch'].gym)
        except Gym_Training_plans.DoesNotExist :
            return None 
        
        Gym_plans_Clients.objects.create(
            client = data['client'],
            gym_training_plan = check_plan,
        )
        
        
        