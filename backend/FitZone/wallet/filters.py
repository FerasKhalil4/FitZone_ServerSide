import django_filters
from .models import Wallet


class ClientFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='client__user__username',lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name='client__user__first_name',lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='client__user__last_name',lookup_expr='icontains')
    
    class Meta:
        model = Wallet
        fields = ['username','first_name','last_name']
    
