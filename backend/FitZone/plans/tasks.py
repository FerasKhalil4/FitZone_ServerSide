from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime
from .models import Gym_plans_Clients,Client_Trianing_Plan
from nutrition.models import NutritionPlan
from django.core.exceptions import ValidationError

@shared_task
def deactivate_plans():
    try:
        now = datetime.now().date()
        check_expired_gym_plans = Gym_plans_Clients.objects.filter(end_date__lt = now)
        check_expired_gym_plans.update(is_active=False)
        check_expired_clients_plans = Client_Trianing_Plan.objects.filter(end_date__lt = now)
        check_expired_clients_plans.update(is_active=False)
        check_expired_meal_plans = NutritionPlan.objects.filter(end_date__lt = now)
        check_expired_meal_plans.update(is_active=False)
        return True
    except Exception as e:
        raise ValidationError(str(e))