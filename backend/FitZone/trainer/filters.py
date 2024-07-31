import django_filters
from .models import Client_Trainer

class Client_TrainerFilter(django_filters.FilterSet):
    registration_status = django_filters.CharFilter(field_name='registration_status',lookup_expr='exact')
    registration_type = django_filters.CharFilter(method='get_registration_type')
    class Meta:
        model = Client_Trainer
        fields = ['registration_status','registration_type']
    def get_registration_type(self,queryset,name,value):
        return queryset.filter(registration_type__exact=value).exclude(registration_status='rejected')
        