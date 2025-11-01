from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import F

from apps.products.models import Product
from apps.suppliers.models import Supplier
from .models import StockMovement
from .forms import StockMovementForm



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
        total_movements = StockMovement.objects.count()

        # Conta produtos com estoque baixo ou zerado
        low_stock_count = Product.objects.filter(stock_quantity__lte=F('minimum_stock')).count()

        # Busca as 10 movimentações mais recentes
        recent_activities = StockMovement.objects.select_related('product', 'user').order_by('-created_at')[:10]

        context.update({
            'total_products': total_products,
            'total_suppliers': total_suppliers,
            'low_stock_count': low_stock_count,
            'total_movements': total_movements,
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


class MovementCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Criação Movimentação"""
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'inventory/movement_create.html'
    success_url = reverse_lazy('inventory:movement_list')
    # success_url = reverse_lazy('inventory:dashboard')
    success_message = "Movimentação de estoque registrada com sucesso."

    def form_valid(self, form):
        """
        Sobrescreve o método para associar o usuário e atualizar o estoque
        do produto de forma atômica
        """

        # Associa o usuário logado à movimentação
        form.instance.user = self.request.user

        # Usa uma transação para garantir a consistência dos dados
        with transaction.atomic():
            response = super().form_valid(form)

            movement = self.object
            product = movement.product

            if movement.movement_type == StockMovement.IN:
                product.stock_quantity = F('stock_quantity') + movement.quantity
            elif movement.movement_type == StockMovement.OUT:
                product.stock_quantity = F('stock_quantity') - movement.quantity
            elif movement.movement_type == StockMovement.ADJ:
                product.stock_quantity = F('stock_quantity') + movement.quantity  # Ajuste pode ser positivo ou negativo
            
            product.save()
        
        return response

    


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
