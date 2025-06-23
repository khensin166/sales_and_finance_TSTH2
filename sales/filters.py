import django_filters # pylint: disable=import-error
from .models import SalesTransaction

class SalesTransactionFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='transaction_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='transaction_date', lookup_expr='lte')
    payment_method = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = SalesTransaction
        fields = ['payment_method', 'start_date', 'end_date']