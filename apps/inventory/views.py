from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView, DetailView
from django.views.decorators.cache import cache_page
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import F, Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from apps.products.models import Product
from apps.suppliers.models import Supplier
from apps.accounts.mixins import StaffOrAboveRequiredMixin
from .models import StockMovement
from .forms import StockMovementForm
from .filters import StockMovementFilter



# Create your views here.
# --- Views do Inventory ---
class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard"""
    template_name = 'inventory/dashboard.html'

    # Adiciona métricas ao contexto
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Consultas dinâmicas para as métricas
        total_products = Product.objects.count()
        total_suppliers = Supplier.objects.count()
        total_movements = StockMovement.objects.count()

        # Conta produtos com estoque baixo ou zerado
        low_stock_products = Product.objects.low_stock().select_related('category')
        low_stock_count = low_stock_products.count()

        # Busca as 10 movimentações mais recentes (MÉTRICA)
        recent_activities = StockMovement.objects.select_related('product', 'user').order_by('-created_at')[:10]
        # recent_activities = StockMovement.objects.select_related('product', 'user').only(
        #     'id', 'created_at', 'movement_type', 'quantity', 'reason',
        #     'product__name', 'product__sku',
        #     'user__username', 'user__first_name', 'user__last_name'
        # ).order_by('-created_at')[:10]

        # Usuários Ativos (MÉTRICA)
        active_users_count = User.objects.filter(is_active=True).count()

        # Atualiza o contexto com as métricas (context = dicionário que armazena dados para a view renderizar)
        context.update({
            'total_products': total_products,
            'total_suppliers': total_suppliers,
            'low_stock_count': low_stock_count,
            'low_stock_products': low_stock_products[:5],   # <-- aparece 5 produtos abaixo do estoque
            'total_movements': total_movements,
            'recent_activities': recent_activities,
            'active_users': active_users_count,
        })
        return context



class MovementListView(LoginRequiredMixin, ListView):
    """Lista Movimentação"""
    model = StockMovement
    template_name = 'inventory/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 20

    # Filtro de busca e tipo (get_queryset = é um método que retorna o conjunto de dados a ser exibido na view)
    def get_queryset(self):
        """ Sobrescreve o queryset para aplicar filtros de busca e tipo """
        
        queryset = super().get_queryset().select_related('product__category', 'user').order_by('-created_at')

        self.filter = StockMovementFilter(self.request.GET, queryset=queryset)
        return self.filter.qs
    
    # Adiciona o filtro ao contexto (get_context_data = é um método que adiciona dados adicionais ao contexto da view)
    def get_context_data(self, **kwargs):
        """ Adiciona o objeto de filtro ao contexto """
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        context['page_sizes'] = [20, 50, 100]
        context['current_page_size'] = int(self.request.GET.get('page_size', 20))
        return context
    
    # Permite paginação dinâmica via query parameter
    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)



# Cache de 5 minutos para impedir múltiplas consultas idênticas em curto período
@method_decorator(cache_page(60 * 5), name='dispatch')  # Cache de 5 minutos
class MovementAutocompleteView(View):
    """
    API endpoint para autocomplete de movimentações.
    Busca por: nome do produto, SKU, tipo de movimentação, usuário.
    """

    # GET method para busca de movimentações
    def get(self, request):
        query = request.GET.get('q', '').strip()

        # Retorna vazio se query muito curta
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        # Busca movimentações (case-insensitive, busca parcial)
        movements = StockMovement.objects.filter(
            Q(product__name__icontains=query) |
            Q(product__sku__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(reason__icontains=query)
        ).select_related(
            'product', 'user'
        ).only(
            'id', 'created_at', 'movement_type', 'quantity', 'reason',
            'product__name', 'product__sku',
            'user__username', 'user__first_name', 'user__last_name'
        ).order_by('-created_at')[:10]      # Limita a 10 resultados mais recentes

        # Mapeamento de tipos para display
        type_display = {
            'IN': 'Entrada',
            'OUT': 'Saída',
            'ADJ': 'Ajuste'
        }

        # Formata resultados como JSON
        results = []
        for movement in movements:
            user_display = movement.user.get_full_name() or movement.user.username

            results.append({
                'id': movement.id,
                'product_name': movement.product.name,
                'product_sku': movement.product.sku,
                'movement_type': movement.movement_type,
                'movement_type_display': type_display.get(movement.movement_type, movement.movement_type),
                'quantity': movement.quantity,
                'user': user_display,
                'reason': movement.reason or 'Sem motivo',
                'created_at': movement.created_at.strftime('%d/%m/%Y %H:%M'),
                'url': f'/inventory/movements/{movement.id}/'
            })
        
        # Retorna resposta JSON com resultados e contagem
        return JsonResponse({
            'results': results,
            'count': len(results),
            'query': query
        })



class MovementCreateView(StaffOrAboveRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Criação Movimentação"""
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'inventory/movement_create.html'
    success_url = reverse_lazy('inventory:movement_list')
    # success_url = reverse_lazy('inventory:dashboard')
    success_message = "Movimentação de estoque registrada com sucesso."

    # Passa o usuário logado para o formulário para validações específicas
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # Sobrescreve o método para associar o usuário e atualizar o estoque do produto
    def form_valid(self, form):
        """
        Sobrescreve o método para associar o usuário e atualizar o estoque
        do produto de forma atômica
        """

        # Associa o usuário logado à movimentação
        form.instance.user = self.request.user

        # Usa uma transação para garantir a consistência dos dados (movimentação + atualização de estoque)
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

    # Otimiza a consulta para incluir dados do produto e do usuário
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

    # Retorna produtos com estoque baixo para Dashboard
    def get_queryset(self):
        # Retorna produtos com estoque baixo para Dashboard
        return Product.objects.low_stock().select_related('category').order_by('stock_quantity')
