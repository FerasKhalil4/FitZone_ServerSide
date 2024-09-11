import django_filters
from user.models import User
from .models import Gym,Shifts,Employee


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username',lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name='first_name',lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='last_name',lookup_expr='icontains')
    
    class Meta:
        model = User
        fields = ['username','first_name','last_name']
    

class GymFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',lookup_expr='icontains')
    
    class Meta:
        model = Gym
        fields =['name']

class EmployeeFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='employee__user__username',lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name='employee__user__first_name',lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='employee__user__last_name',lookup_expr='icontains')
    
    class Meta:
        model = Shifts
        fields = ['username','first_name','last_name']
        
        
class TrainerFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='user__username',lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name='user__first_name',lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='user__last_name',lookup_expr='icontains')
    
    class Meta:
        model = Employee
        fields = ['username','first_name','last_name']
        