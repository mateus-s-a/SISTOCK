import django_filters
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """
    FilterSet para o modelo Product. Permite filtrar por nome e categoria.
    """

    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Nome do Produto',
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label='Categoria',
    )

    class Meta:
        model = Product
        fields = ['name', 'category']
        