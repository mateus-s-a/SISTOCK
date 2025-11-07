from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import F, Q

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
        low_stock_products = Product.objects.low_stock().select_related('category')
        low_stock_count = low_stock_products.count()

        # Busca as 10 movimentações mais recentes
        recent_activities = StockMovement.objects.select_related('product', 'user').order_by('-created_at')[:10]

        context.update({
            'total_products': total_products,
            'total_suppliers': total_suppliers,
            'low_stock_count': low_stock_count,
            'low_stock_products': low_stock_products[:5],   # <- 5 produtos abaixo do estoque
            'total_movements': total_movements,
            'recent_activities': recent_activities,
        })
        return context



class MovementListView(LoginRequiredMixin, ListView):
    """Lista Movimentação"""
    model = StockMovement
    template_name = 'inventory/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 20

    def get_queryset(self):
        """
        Sobrescreve o queryset para aplicar filtros de busca e tipo
        """
        queryset = super().get_queryset().select_related('product', 'user').order_by('-created_at')
        
        # Filtro por produto (nome ou SKU)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(product__name__icontains=query) | Q(product__sku__icontains=query)
            )
        
        # Filtro por tipo de movimentação
        movement_type = self.request.GET.get('type')
        if movement_type in dict(StockMovement.MOVEMENT_TYPES):
            queryset = queryset.filter(movement_type=movement_type)
        
        return queryset



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



class MovementDetailView(LoginRequiredMixin, DetailView):
    """Detalhe Movimentação"""
    model = StockMovement
    template_name = 'inventory/movement_detail.html'
    context_object_name = 'movement'

    def get_queryset(self):
        """
        Otimiza a consulta para incluir dados do produto e do usuário
        """
        return super().get_queryset().select_related('product', 'user')



class StockAlertsView(LoginRequiredMixin, ListView):
    """Alerta Estoque Baixo"""
    model = Product
    template_name = 'inventory/stock_alerts.html'
    context_object_name = 'low_stock_products'
    paginate_by = 20

    def get_queryset(self):
        # Retorna produtos com estoque baixo para Dashboard
        return Product.objects.low_stock().select_related('category').order_by('stock_quantity')
