from .models import *
from wallet.models import *
from classes.models import Client_Class
from datetime import datetime
from django.db.models import Q 
from points.models import Points
from django.db import transaction
from dateutil.relativedelta import relativedelta


class SubscripeWithTrainerService():
    
    @staticmethod
    def get_points(total) -> int:
        points = Points.objects.get(activity = 'Purchasing').points_percentage
        return total // points
        
    
    @staticmethod
    def check_overlap_query(client,days_off,start_hour,end_hour,now) -> None:
        
        end_date = now + relativedelta(months = 1)
        query = Q(
            client = client,
            is_deleted=False
        )
        date_query = query & (
        Q(
            class_id__start_date__lte = now,
            class_id__end_date__gt = now
        )|Q(
            class_id__start_date__lt = end_date,
            class_id__end_date__gte = end_date
        ) | Q(
            class_id__start_date__gte = now,
            class_id__end_date__lte = end_date,
        )
         )
        
        time_overlap =date_query & (
            Q(
            class_id__start_time__lte = start_hour,
            class_id__end_time__gt = start_hour,
        ) |Q(
            class_id__start_time__lt = end_hour,
            class_id__end_time__gte = end_hour,   
        )|Q(
            class_id__start_time__gte = start_hour,
            class_id__end_time__lte = end_hour,  
        )
                        )
        
        day_overlap_query = Q()
        for day,day_name in days_off.items():
            day_overlap_query |= ~Q(
                class_id__days_of_week__contains = {day:day_name}
            )
        day_overlap_query = time_overlap & day_overlap_query 

        check = Client_Class.objects.filter(day_overlap_query)
        
        if check.exists():
            raise ValidationError('there is an overlap in the client schedule between the courses and the private group he registered into')
    
    @staticmethod
    def check_group(group,now)->None:
        query = Q(
            start_date__lte = now,
            end_date__gte = now,
            group = group.pk,
            registration_status = 'accepted',
            is_deleted=False
        )
        group_current_capacity = Client_Trainer.objects.filter(query).count()
        
        if group_current_capacity >= group.group_capacity:
            raise ValidationError('this group is full try another one')
        
    
    @staticmethod
    def client_payment_points(client,total,points) -> None:
        wallet = Wallet.objects.get(client=client)
        
        if (total > wallet.balance) and (total > 0): 
            raise ValueError('insufficient amount of money in the clients wallet')
        print(wallet.balance)
        wallet.balance -= total
        print(wallet.balance)
        
        wallet.save ()
        print(client.points)
        client.points += points
        print(client.points)
        
        client.save()
        
        if total != 0:
            if total < 0:
                tranasaction_type = 'retrieve'
            elif total > 0:
                tranasaction_type = 'cut'
            print(tranasaction_type)
        
            Wallet_Deposit.objects.create(
                client = client,
                amount = total,
                tranasaction_type = tranasaction_type
            )

        
    @staticmethod 
    def check_client_trainer(branch) -> None:
        check = Shifts.objects.filter(branch=branch,is_active=True)
        if not check.exists():
           raise ValidationError('client is not subscribed with the same gym as the trainer') 
    
    @staticmethod 
    def check_client_sub_overlap(client,now) -> Q:
        
        base_query = Q(
            client=client
            ,start_date__lte = now,
            end_date__gte=now,
            registration_status = 'accepted'
        )
        query = base_query | Q(
            client=client,
            registration_status = 'pending',
        )
        query &= Q(
            is_deleted = False
        )
        
        return query
        
        
    @staticmethod
    def subscripe_with_trainer(data) -> Client_Trainer:
        print(data)
        client = data.pop('client')
        trainer = data.pop('trainer')
        registration_type = data.pop('registration_type')
        group = data.pop('group',None)
        branch = data.pop('branch',None)
        now =  datetime.now().date()
        payment_total = trainer.private_training_price if group is not None else trainer.online_training_price
        
        query = SubscripeWithTrainerService.check_client_sub_overlap(client,now)
        check = Client_Trainer.objects.filter(query)
        if check.exists():
            raise ValidationError('this client is already registered or in pending state with some trainer')
        
        if group is not None:
            
            SubscripeWithTrainerService.check_client_trainer(branch)
            SubscripeWithTrainerService.check_group(group,now)
            
            SubscripeWithTrainerService.check_overlap_query(client,group.days_off,group.start_hour,group.end_hour,now)

        points = int(SubscripeWithTrainerService.get_points(payment_total))

        SubscripeWithTrainerService.client_payment_points(client,payment_total,points)
        
        return Client_Trainer.objects.create(
            client = client,
            trainer = trainer, 
            registration_type = registration_type,
            group = group,
        )
            
        
class UpdateSubscriptionWithTrainerService():
    
    @staticmethod
    def update_sub(data,instance):
        try:
            with transaction.atomic():
                group = data.pop('group', None)
                registration_type = data.pop('registration_type', None)
                client = data.pop('client', None)
                branch = data.pop('branch',None)
                trainer = data.pop('trainer')
                now =  datetime.now().date()
                payment_total = trainer.private_training_price if registration_type == 'private'  else trainer.online_training_price
                old_payment = trainer.private_training_price if instance.registration_type == 'private' else trainer.online_training_price
                total = payment_total - old_payment
                updated_data = {}
                
                if instance.registration_status != 'rejected':
                    if group is not None:
                        old_group_number = instance.group.pk if instance.group is not None else None
                        if group.pk != old_group_number:
                            SubscripeWithTrainerService.check_client_trainer(branch)
                            SubscripeWithTrainerService.check_group(group,now)
                            
                            SubscripeWithTrainerService.check_overlap_query(client,group.days_off,group.start_hour,group.end_hour,now)
                            updated_data['group'] = group
                            updated_data['old_group_number'] = old_group_number
                            
                        
                    if instance.registration_status == 'pending' and ((instance.start_date is None) and (instance.end_date is None)):
                        updated_data['registration_type'] = registration_type
                        points = int(SubscripeWithTrainerService.get_points(total))
                        SubscripeWithTrainerService.client_payment_points(client,total,points)
                        updated_data['is_updated'] = True
                        
                    
                    updated_data['registration_status'] = 'pending'
 
                    for attr, value in updated_data.items():
                        setattr(instance,attr,value)
                    
                    instance.save()
                    
                    return instance
                else:
                    raise ValidationError('this client is already rejected in this process')
        except Exception as e:
            raise ValueError(str(e))
        

class DeleteSubscriptionWihtTrainerService():
    
    @staticmethod
    def delete_sub(instance,client):
        try:
            with transaction.atomic():

                if instance.registration_status == 'pending':
                    payment_total = -(instance.trainer.private_training_price if instance.registration_type == 'private' else instance.trainer.online_training_price)
                    instance.registration_status = 'rejected'
                    instance.is_deleted = True
                    
                    instance.save()
                    
                    points = int(SubscripeWithTrainerService.get_points(payment_total))
                    
                    SubscripeWithTrainerService.client_payment_points(client,payment_total,points)
                    return instance
                    
                else:
                    raise ValidationError(f'you cannot delete your sub with this trainer as the registrations status is {instance.registration_status}')
        except Exception as e:
            raise ValueError(str(e))
        