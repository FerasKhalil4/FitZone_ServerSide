from __future__ import absolute_import,unicode_literals
from celery import shared_task
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import *
from wallet.models import Wallet,Wallet_Deposit
from gym.models import Trainer
from django.core.exceptions import ValidationError

@shared_task
def reject_expired_requests():
    try:
        now = datetime.datetime.now().date()
        requests = Client_Trainer.objects.filter(registration_status = 'pending',is_updated=False,is_deleted=False)
        for request in requests:
            trainer = Trainer.objects.get(pk=request.trainer.pk)
            expired_time = request.created_at + relativedelta(days=3)
            if now > expired_time :
                request.registration_status = 'rejected'
                request.rejection_reason = 'expired request with no trainer response'
                request.save()
                wallet = Wallet.objects.get(client=request.client.pk)
                fee = trainer.private_training_price if request.registration_type =='private' else trainer.online_training_price
                wallet.balance += fee
                wallet.save()
                
                Wallet_Deposit.objects.create(
                    client=request.client,
                    tranasaction_type = 'retrieve',
                    amount = fee
                )
                
    except Exception as e:
        raise ValidationError(str(e))
    
            
        