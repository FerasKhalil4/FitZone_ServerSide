from __future__ import unicode_literals,absolute_import
from .models import Offer
from celery import shared_task
from datetime import datetime

@shared_task
def deactivated_expired_offers():
    now = datetime.now().date()
    expired_offers = Offer.objects.select_for_update().filter(end_date__lt=now,is_deleted=False)
    for offer in expired_offers:
        offer.is_deleted = True
        offer.save()
        