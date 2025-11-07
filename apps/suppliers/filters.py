import django_filters
from .models import Supplier


class SupplierFilter(django_filters.FilterSet):
    """
    Filtra por nome, email e CNPJ
    """
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Nome do Fornecedor'
    )
    email = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Email'
    )
    cnpj = django_filters.CharFilter(
        lookup_expr='icontains',
        label='CNPJ'
    )

    class Meta:
        model = Supplier
        fields = ['name', 'email', 'cnpj']
