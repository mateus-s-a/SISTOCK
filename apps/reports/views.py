from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
import csv

from apps.products.models import Product
from apps.inventory.models import StockMovement

# Create your views here.


# -- Views de Relatórios --
class ReportIndexView(LoginRequiredMixin, TemplateView):
    """Índice Relatórios"""
    template_name = 'reports/report_index.html'


class StockReportView(LoginRequiredMixin, ListView):
    """Relatório Estoque"""
    model = Product
    template_name = 'reports/stock_report.html'
    context_object_name = 'products'
    paginate_by = 50

    def get_queryset(self):
        """
        Retorna produtos com cálculo de valor em estoque
        """
        queryset = Product.objects.select_related('category').annotate(
            total_value=ExpressionWrapper(
                F('stock_quantity') * F('price'),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        ).order_by('name')

        # Filtro por status estoque
        status = self.request.GET.get('status')
        if status == 'low':
            queryset = queryset.filter(stock_quantity__lte=F('minimum_stock'))
        elif status == 'out':
            queryset = queryset.filter(stock_quantity=0)
        elif status == 'ok':
            queryset = queryset.filter(stock_quantity__gt=F('minimum_stock'))

        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Adiciona estatísticas gerais ao contexto.
        """
        context = super().get_context_data(**kwargs)

        # Calcula totais gerais
        all_products = Product.objects.all()
        context['total_products'] = all_products.count()
        context['total_stock_value'] = sum(
            p.stock_quantity * p.price for p in all_products
        )
        context['low_stock_count'] = Product.objects.filter(
            stock_quantity__lte=F('minimum_stock')
        ).count()

        return context


class MovementReportView(LoginRequiredMixin, TemplateView):
    """Relatório Movimentações"""
    template_name = 'reports/movement_report.html'


def export_stock_csv(request):
    """Export CSV Estoque"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="relatorio_estoque.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Produto', 'SKU', 'Categoria',
        'Estoque Atual', 'Estoque Mínimo',
        'Preço Unit.', 'Valor Total', 'Status'
    ])

    # Busca produtos do banco
    products = Product.objects.select_related('category').annotate(
        total_value=ExpressionWrapper(
            F('stock_quantity') * F('price'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )

    for product in products:
        # Determina status
        if product.stock_quantity == 0:
            status = 'Sem Estoque'
        elif product.stock_quantity <= product.minimum_stock:
            status = 'Estoque Baixo'
        else:
            status = 'Normal'
        
        writer.writerow([
            product.name,
            product.sku,
            product.category.name,
            product.stock_quantity,
            product.minimum_stock,
            f'{product.price:.2f}',
            f'{product.total_value:.2f}',
            status,

        ])

    return response


def export_movements_csv(request):
    """Export CSV Movimentos"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="movimentacoes.csv"'

    # TESTE-ESTÁTICO-CSV-MOVIMENTOS => (Relatório Movimentos)
    writer = csv.writer(response)
    writer.writerow(['Data', 'Produto', 'Tipo', 'Quantidade'])
    writer.writerow(['22/10/2025', 'Produto A', 'Entrada', '50'])
    writer.writerow(['21/10/2025', 'Produto B', 'Saída', '15'])

    return response
