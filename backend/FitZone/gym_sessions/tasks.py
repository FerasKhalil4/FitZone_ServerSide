from __future__ import absolute_import, unicode_literals
from celery import shared_task
from gym.models import Branch
from .models import Gym_Subscription
from gym.models import Branch
from django.core.exceptions import ValidationError
from datetime import datetime


@shared_task
def deactivate_subs():
    print('update start')
    now =datetime.now().date()

    try:
        expired_subs = Gym_Subscription.objects.filter(end_date__lt = now,is_active = True)
        expired_subs.update(is_active=False)
            
        branches = Branch.objects.all()
        for branch in branches:
            branch_subs_count = expired_subs.filter(branch=branch.pk).count()
            branch.current_number_of_clients -= branch_subs_count
            branch.save()
        print('success')
    except Exception as e: 
        return ({'error':str(e)})

    
    
    
