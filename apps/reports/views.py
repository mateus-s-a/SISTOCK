from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, ExpressionWrapper, DecimalField
import csv

from apps.products.models import Product
from apps.inventory.models import StockMovement
from datetime import datetime, timedelta
from django.utils import timezone

# Create your views here.


# -- Views de Relatórios --
class ReportIndexView(LoginRequiredMixin, TemplateView):
    """Índice Relatórios"""
    template_name = 'reports/report_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Total de produtos
        context['total_products'] = Product.objects.count()

        # Valor total em estoque
        products = Product.objects.annotate(
            total_value=ExpressionWrapper(
                F('stock_quantity') * F('price'),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        )
        context['total_stock_value'] = sum(p.total_value for p in products)

        # Produtos em alerta (baixo estoque)
        context['low_stock_count'] = Product.objects.filter(
            stock_quantity__lte=F('minimum_stock')
        ).count()

        # Movimentações neste mês
        start_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        context['monthly_movements'] = StockMovement.objects.filter(created_at__gte=start_month).count()

        return context


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

        # Calcula o valor total da página atual
        page_products = context['products']     # -> queryset da pág atual
        context['page_total_value'] = sum(
            product.stock_quantity * product.price for product in page_products
        )

        return context


class MovementReportView(LoginRequiredMixin, ListView):
    """Relatório Movimentações"""
    model = StockMovement
    template_name = 'reports/movement_report.html'
    context_object_name = 'movements'
    paginate_by = 50

    def get_queryset(self):
        """
        Retorna movimentações filtradas por data e tipo
        """
        queryset = StockMovement.objects.select_related('product', 'user').order_by('-created_at')

        # Filtro por período
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')

        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=start)
            except ValueError:
                pass    # <- ignore se formato inválido
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d')
                end = end + timedelta(days=1)   # <- add 1 dia para incluir todo o dia final
                queryset = queryset.filter(created_at__lt=end)
            except ValueError:
                pass    # <- ignore se formato inválido
        
        if start_date and end_date:
            if end > start:
                queryset = queryset.filter(created_at__range=[start, end])
        
        # Filtro tipo movimentação
        movement_type = self.request.GET.get('type')
        if movement_type in dict(StockMovement.MOVEMENT_TYPES):
            queryset = queryset.filter(movement_type=movement_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Adiciona estatísticas ao contexto
        """
        context = super().get_context_data(**kwargs)

        # Calcula totais baseados no queryset filtrado
        movements = self.get_queryset()

        context['total_movements'] = movements.count()
        context['total_in'] = movements.filter(movement_type='IN').count()
        context['total_out'] = movements.filter(movement_type='OUT').count()
        context['total_adj'] = movements.filter(movement_type='ADJ').count()

        # Preserva valores dos filtros para os campos
        context['start_date'] = self.request.GET.get('start', '')
        context['end_date'] = self.request.GET.get('end', '')
        context['selected_type'] = self.request.GET.get('type', '')

        return context


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
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="relatorio_movimentacoes.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Data/Hora', 'Produto', 'SKU',
        'Tipo', 'Quantidade', 'Responsável',
        'Motivo'
    ])

    # Busca movimentações com mesmos filtros da view
    movements = StockMovement.objects.select_related('product', 'user').order_by('-created_at')

    # Aplica filtros data
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            movements = movements.filter(created_at__gte=start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end + timedelta(days=1)
            movements = movements.filter(created_at__lt=end)
        except ValueError:
            pass
    
    # Aplica filtro de tipo
    movement_type = request.GET.get('type')
    if movement_type in dict(StockMovement.MOVEMENT_TYPES):
        movements = movements.filter(movement_type=movement_type)
    
    # Escreve dados
    for movement in movements:
        tipo_display = movement.get_movement_type_display()
        quantidade = f"-{movement.quantity}" if movement.movement_type == 'OUT' else str(movement.quantity)

        writer.writerow([
            movement.created_at.strftime('%d/%m/%Y %H:%M'),
            movement.product.name,
            movement.product.sku,
            tipo_display,
            quantidade,
            movement.user.username,
            movement.reason or '-'
        ])

    return response
