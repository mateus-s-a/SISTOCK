import django_filters
from .models import StockMovement
from apps.products.models import Product


class StockMovementFilter(django_filters.FilterSet):
    """
    Filtra por produto, tipo e usuário
    """
    product = django_filters.ModelChoiceFilter(
        queryset=Product.objects.all(),
        label='Produto'
    )
    movement_type = django_filters.ChoiceFilter(
        choices=StockMovement.MOVEMENT_TYPES,
        label='Tipo de Movimentação'
    )
    user__username = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Usuário'
    )
    created_at = django_filters.DateFromToRangeFilter(
        label='Período'
    )

    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'user__username']
