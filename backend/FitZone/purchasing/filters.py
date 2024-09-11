from django_filters import rest_framework as filters
from store.models import Product

class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    brand = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Product
        fields = ['name', 'brand']
        
    def filter_recent(self, queryset, name, value):
        try:
            view = self.request.view
            extra_param = view.kwargs.get('branch_id') 
            print('-----------------------------')
        except Exception as e:
            raise ValueError(str(e))
    
    