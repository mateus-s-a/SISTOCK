from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import F

from apps.products.models import Product
from apps.suppliers.models import Supplier
from .models import StockMovement



# Create your views here.
# --- Views do Inventory ---
class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard"""
    template_name = 'inventory/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Consultas dinâmicas para as métricas
        total_products = Product.objects.count()
        total_suppliers = Supplier.objects.count()

        # Conta produtos com estoque baixo ou zerado
        low_stock_count = Product.objects.filter(stock_quantity__lte=F('minimum_stock')).count()

        # Busca as 10 movimentações mais recentes
        recent_activities = StockMovement.objects.select_related('product', 'user').order_by('-created_at')[:10]

        context.update({
            'total_products': total_products,
            'total_suppliers': total_suppliers,
            'low_stock_count': low_stock_count,
            'recent_activities': recent_activities,
        })
        return context



class MovementListView(LoginRequiredMixin, TemplateView):
    """Lista Movimentação"""
    template_name = 'inventory/movement_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TESTE-ESTÁTICO-INVENTORY => Dados fictícios (Lista Movimentação)
        context['movements'] = [
            {'id': 1, 'product': 'Produto A', 'type': 'Entrada', 'quantity': 50, 'date': '22/10/2025'},
            {'id': 2, 'product': 'Produto B', 'type': 'Saída', 'quantity': 15, 'date': '21/10/2025'},
        ]
        return context


class MovementCreateView(LoginRequiredMixin, TemplateView):
    """Criação Movimentação"""
    template_name = 'inventory/movement_create.html'

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Movimentação registrada com sucesso. (Simulação)')
        return redirect('inventory:movement_list')


class MovementDetailView(LoginRequiredMixin, TemplateView):
    """Detalhe Movimentação"""
    template_name = 'inventory/movement_detail.html'


class StockAlertsView(LoginRequiredMixin, TemplateView):
    """Alerta Estoque Baixo"""
    template_name = 'inventory/stock_alerts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TESTE-ESTÁTICO-INVENTORY => Dados fictícios (Alerta Estoque Baixo)
        context['low_stock_products'] = [
            {'name': 'Produto X', 'current_stock': 5, 'minimum_stock': 10},
            {'name': 'Produto Y', 'current_stock': 2, 'minimum_stock': 15},
        ]
        return context
