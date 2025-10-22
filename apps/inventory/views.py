from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Create your views here.

class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard"""
    template_name = 'inventory/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TESTE-ESTÁTICO-INVENTORY => Dados fictícios (Dashboard)
        context.update({
            'total_products': 125,
            'low_stock_count': 8,
            'total_movements': 350,
            'recent_activities': [
                {'action': 'Entrada', 'product': 'Produto A', 'quantity': 50, 'date': '22/10/2025'},
                {'action': 'Saída', 'product': 'Produto B', 'quantity': 15, 'date': '21/10/2025'},
                {'action': 'Ajuste', 'product': 'Produto C', 'quantity': -2, 'date': '20/10/2025'},
            ]
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
