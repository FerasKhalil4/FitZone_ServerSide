from .models import *
from trainer.models import Client_Trainer
from offers.models import Percentage_offer
from django.db import transaction
from datetime import datetime
from django.db.models import Q 
from django.core.exceptions import ValidationError
from trainer.services import SubscripeWithTrainerService
from purchasing.services.private_store_service import PrivateStoreService

class RegistrationClassService():
    
    @staticmethod 
    def check_percentage_offers(now,branch,pk) -> int: 
        discount = 0
        
        try:
            discount  = Percentage_offer.objects.get(
                offer__start_date__lte = now,
                offer__end_date__gte = now,
                offer__is_deleted=False,
                offer__branch = branch,
                class_id = pk
            ).percentage_cut
        except Percentage_offer.DoesNotExist:
            print('no offer found')
            pass
        
        return discount
    
    @staticmethod
    def check_client_schedule_overlap(client,schdule,pk=None)->None:

        query = (
            Q(
            class_id__start_date__lte = schdule.start_date,
            class_id__end_date__gt = schdule.start_date,
        )|Q(
            class_id__start_date__lt = schdule.end_date,
            class_id__end_date__gte = schdule.end_date,
        )|Q(
            class_id__start_date__lte = schdule.start_date,
            class_id__end_date__gte = schdule.end_date,
        )
            )
        query &= (
            Q(
                class_id__start_time__lte = schdule.start_time,
                class_id__end_time__gt = schdule.start_time,
            )|Q(
                class_id__start_time__lt = schdule.end_time,
                class_id__end_time__gte = schdule.end_time,
            ) | Q(
                class_id__start_time__lte = schdule.start_time,
                class_id__end_time__gte = schdule.end_time,
            )
        )
        day_of_week_query = Q()
        for day, name in schdule.days_of_week.items():
            day_of_week_query |= Q(
                class_id__days_of_week__contains = {day:name}
            ) 
        query &= day_of_week_query
        query &= Q(
            client=client,
            is_deleted=False
        )
        if pk is not None:
            query &= ~Q(
                pk = pk
            )
        check = Client_Class.objects.filter(query)
        
        if check.exists():
            raise ValidationError('this client is registered in a class that overlaps with this class')
        
    @staticmethod
    def check_private_training_overlap(client, schdule) -> None:

        query = (
            Q(
            start_date__lte = schdule.start_date,
            end_date__gt = schdule.start_date,
        )|Q(
            start_date__lt = schdule.end_date,
            end_date__gte = schdule.end_date,
        )|Q(
            start_date__lte = schdule.start_date,
            end_date__gte = schdule.end_date,
        )
            )
        query &= (
            Q(
                group__start_hour__lte = schdule.start_time,
                group__end_hour__gt = schdule.start_time,
            )|Q(
                group__start_hour__lt = schdule.end_time,
                group__end_hour__gte = schdule.end_time,
            ) | Q(
                group__start_hour__lte = schdule.start_time,
                group__end_hour__gte = schdule.end_time,
            )
        )
        
        day_overlap_query = Q()
        for day,day_name in schdule.days_of_week.items():
            day_overlap_query |= ~Q(
                group__days_off__contains = {day:day_name}
            )
        query &= day_overlap_query
        
        query &= ~Q(
            registration_status = 'rejected'
            )
        query &= Q(
            client = client,
            is_deleted = False
        )
        
        check = Client_Trainer.objects.filter(query)
        
        if check.exists():
            raise ValidationError('this client is registered with a trainer at the same time of the registered class')

    @staticmethod
    def register(data)-> Client_Class:
        try:
            with transaction.atomic() :
                
                now =datetime.now().date()
                client = data.pop('client', None)
                schdule = data.pop('class_id',None)
                vouchers = data.pop('vouchers',None)
                base_total = schdule.class_id.registration_fee
                points = schdule.class_id.points
                
                RegistrationClassService.check_client_schedule_overlap(client,schdule)
                RegistrationClassService.check_private_training_overlap(client,schdule)
                discount = PrivateStoreService.check_voucher(client,vouchers,now)

                discount = (100 - (discount + RegistrationClassService.check_percentage_offers(now,schdule.class_id.branch,schdule.pk))) / 100
                offered_total = base_total * discount
                
                SubscripeWithTrainerService.client_payment_points(client,offered_total,points)
                
                instance = Client_Class.objects.create(
                    client=client,
                    class_id = schdule,
                    total = base_total,
                    offered_total = offered_total,
                    retrieved_reason = ""
                )
                
                schdule.current_number_of_trainees += 1
                schdule.save()
                
                return instance
        
        except Exception as e:
            raise ValueError(str(e))
        
class UpdateRegistrationService():
    
    @staticmethod
    def retireved_value(instance,base_total) -> float:
        
        if base_total < 0:
            gym_pecentage = (100 - instance.class_id.class_id.branch.gym.cut_percentage) / 100
            print(gym_pecentage)
            if 1 > gym_pecentage > 0 :
                base_total *= gym_pecentage
            elif gym_pecentage == 1:
                base_total = 0 
            elif gym_pecentage is None or gym_pecentage == 0:
                ...
        else:
            base_total = 0
            
        print(base_total)
        return base_total
    
    @staticmethod
    def check_class_availabilty(schdule) -> None:
        if schdule.current_number_of_trainees >= schdule.allowed_number_for_class:
            raise ValueError("class is full try another one")
        
        
    @staticmethod
    
    def update_schdeule_capacity(instance,amount) -> None:
                        
        print('----------------------------------------------------------------')
        print(instance.class_id.pk)
        schedule = Class_Scheduel.objects.get(pk=instance.pk)
        print(schedule.current_number_of_trainees)
        schedule.current_number_of_trainees += amount
        print(schedule.current_number_of_trainees)
        schedule.save()
        
        
    def update(data,instance) -> Client_Class:

        try:
            with transaction.atomic():
                print(instance)
                print(data)
                new_registered_class = data.pop('class_id')
                
                vouchers = data.pop('vouchers')
                client = data.pop('client')
                now = datetime.now().date()
                previous_total = instance.offered_total if 0 < instance.offered_total < instance.total else instance.total
                points = new_registered_class.class_id.points - instance.class_id.class_id.points
                
                UpdateRegistrationService.check_class_availabilty(new_registered_class)
                RegistrationClassService.check_client_schedule_overlap(client,new_registered_class,pk=instance.pk)
                RegistrationClassService.check_private_training_overlap(client,new_registered_class)
                
                discount = PrivateStoreService.check_voucher(client,vouchers,now)
                discount = (100 - (discount + RegistrationClassService.check_percentage_offers(now,new_registered_class.class_id.branch,new_registered_class.pk))) / 100
                
                offered_total = new_registered_class.class_id.registration_fee * discount
                
                new_total = offered_total - previous_total
                
                updated_data = {
                    'class_id':new_registered_class,
                    'total' : new_registered_class.class_id.registration_fee,
                    'offered_total' : offered_total ,
                }
                
                new_total = UpdateRegistrationService.retireved_value(instance,new_total)
                
                SubscripeWithTrainerService.client_payment_points(client,new_total,points)
                    
                updated_data['retrived_money'] = abs(new_total)
                updated_data['retrieved_reason'] = 'Update Registration' if new_total != 0 else None
                
                print(instance.class_id)
                print(new_registered_class)
                UpdateRegistrationService.update_schdeule_capacity(instance.class_id,-1)
                UpdateRegistrationService.update_schdeule_capacity(new_registered_class,1)
                
                for attr, value in updated_data.items():
                    setattr(instance,attr,value)
                instance.save()
                

                
                return instance
                
        except Exception as e:
            raise ValueError(str(e))
        
class DeleteRegistrationService():
    
    
    @staticmethod
    def delete(instance,client) -> None:
        try:
            with transaction.atomic():
                
                total = -(instance.offered_total if  0 < instance.offered_total < instance.total else instance.total)
                new_total = UpdateRegistrationService.retireved_value(instance,total)
                points = -(instance.class_id.class_id.points)
                
                SubscripeWithTrainerService.client_payment_points(client,new_total,points)
                
                instance.is_deleted = True
                instance.retrieved_money = abs(new_total)
                instance.retrieved_reason = 'deleted by client'
                instance.save()
                
                UpdateRegistrationService.update_schdeule_capacity(instance.class_id,-1)
        except Exception as e:
            raise ValueError(str(e))