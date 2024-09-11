from .models import *
from django.db import transaction
from gym.models import Shifts
class RateService():
    
    @staticmethod
    def get_rate_avg(current_rate_avg,total_ratings,new_rating_value,type):
        
        if type == 'add':
            return ((current_rate_avg * total_ratings) + new_rating_value) / (total_ratings + 1)
        elif type == 'substract':
            return ((current_rate_avg * total_ratings) - new_rating_value) / (total_ratings - 1)
            
    
    @staticmethod
    def rate_gym(rate,gym,value):
        GymRate.objects.create(rate=rate , gym=gym)
        new_gym_rate_avg = RateService.get_rate_avg(gym.rate,gym.number_of_rates,value,'add')
        return new_gym_rate_avg
        

    @staticmethod
    def rate_trainer(rate,trainer, value):
        TrainerRate.objects.create(rate=rate , trainer=trainer)
        new_trainer_rate_avg = RateService.get_rate_avg(trainer.rate,trainer.number_of_rates,value,'add')
        return new_trainer_rate_avg

    
    @staticmethod
    def rate(data):
        try:
            with transaction.atomic():
                
                client = data.pop('client')
                gym = data.pop('gym',None)
                trainer = data.pop('trainer',None)
                value = data.pop('value')
                is_app_rate = data.pop('is_app_rate',None)
                
                rate = Rate.objects.create(
                    client = client,
                    value = value,
                )
                
                if gym is not None:
                    gym = Branch.objects.select_for_update().get(pk=gym)
                    avg = RateService.rate_gym(rate,gym,value)
                    gym.rate = avg
                    gym.number_of_rates += 1
                    gym.save()
        
                    
                elif trainer is not None:
                    trainer = Trainer.objects.select_for_update().get(pk=trainer)
                    avg = RateService.rate_trainer(rate,trainer,value)
                            
                    trainer.rate = avg
                    trainer.number_of_rates += 1
                    trainer.save()
                    
                elif is_app_rate is not None:
                    rate.is_app_rate = True
                    rate.save()
                
                return rate
                    
        except Exception as e:
            raise ValueError(str(e))
        
    @staticmethod 
    def get_ratings(user) -> dict:
        try:
            user_role = user.role
            
            if user_role == 1:
                ratings = Rate.objects.all()
                return {
                    'gym_ratings':None,
                    'trainer_ratings':None,
                    'ratings': ratings
                }
            
            elif user_role == 2:
                gym_ratings = GymRate.objects.filter(gym__gym__manager__pk = user.pk,gym__is_active=True)
                ids = [gym['id'] for gym in user.manager.values()]
                trainer_ratings = TrainerRate.objects.filter(trainer__employee__employee__branch__gym__pk__in = ids,trainer__employee__is_active = True)
                return {
                    'gym_ratings':gym_ratings,
                    'trainer_ratings':trainer_ratings,
                    'ratings': None
                }
                
            elif user_role == 3:
                gym_ratings = GymRate.objects.filter(gym__branch__employee__user__pk = user.pk,gym__is_active=True)
                
                ids = [branch['branch_id'] for branch in user.user.employee.values()]
                trainer_ratings = TrainerRate.objects.filter(trainer__employee__employee__branch__pk__in = ids,trainer__employee__employee__is_active = True)

                return {
                    'gym_ratings':gym_ratings,
                    'trainer_ratings':trainer_ratings,
                    'ratings': None
                }
                
            elif user_role == 4:
                trainer_ratings = TrainerRate.objects.filter(trainer__employee__user__pk = user.pk)
                return {
                    'gym_ratings':None,
                    'trainer_ratings':trainer_ratings,
                    'ratings': None
                }
                                    
        except Exception as e:
            raise ValueError(str(e))
        
        
    def update_ratings(instance,value,client) -> Rate:

        try:
            with transaction.atomic():
                instance.is_deleted = True
                instance.save()
                
                rate = Rate.objects.create(
                        client = client,
                        value = value,
                        )
                
                if hasattr(instance,'gym_rate'):
                    gym = Branch.objects.select_for_update().get(pk=instance.gym_rate.gym.pk)
                    RateService.rate_gym(rate,gym,value)
                    
                elif hasattr(instance,'trainer_rate'):
                    
                    trainer = Trainer.objects.select_for_update().get(pk=instance.trainer_rate.trainer.pk)
                    RateService.rate_trainer(rate,trainer,value)
                    
                elif instance.is_app_rate:
                    rate.is_app_rate = True
                    rate.save()
                    
                return rate          
                    
        except Exception as e:
            raise ValueError(str(e))
                    