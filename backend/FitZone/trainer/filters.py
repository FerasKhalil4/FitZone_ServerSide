import django_filters
from .models import Client_Trainer
from gym.models import Trainer

class Client_TrainerFilter(django_filters.FilterSet):
    registration_status = django_filters.CharFilter(field_name='registration_status',lookup_expr='exact')
    registration_type = django_filters.CharFilter(method='get_registration_type')
    class Meta:
        model = Client_Trainer
        fields = ['registration_status','registration_type']
    def get_registration_type(self,queryset,name,value):
        return queryset.filter(registration_type__exact=value).exclude(registration_status='rejected')
        
class TrainerFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='employee__user__username',lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name='employee__user__first_name',lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='employee__user__last_name',lookup_expr='icontains')
    
    class Meta:
        model = Trainer
        fields = ['username','first_name','last_name']
        