from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import GymSubscriptionPricingSerailizer, BranchProductsPricingSerailizer, ClassRegistrationPricingSerailizer
from gym.models import Gym, Branch

class GymSubscriptionPricingUpdateAV(generics.UpdateAPIView):
    queryset = Gym.objects.filter(is_deleted = False)
    serializer_class = GymSubscriptionPricingSerailizer
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

update_gym_subscription_pricing = GymSubscriptionPricingUpdateAV.as_view()


class BranchProductsPricingUpdateAV(generics.UpdateAPIView):
    queryset = Branch.objects.filter(is_active = True ,gym__is_deleted = False)
    serializer_class = BranchProductsPricingSerailizer
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

update_branch_products_pricing = BranchProductsPricingUpdateAV.as_view()

class ClassRegistrationPricingUpdateAV(generics.UpdateAPIView):
    queryset = Branch.objects.filter(is_active = True ,gym__is_deleted = False)
    serializer_class = ClassRegistrationPricingSerailizer
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

update_class_registration_pricing = ClassRegistrationPricingUpdateAV.as_view()