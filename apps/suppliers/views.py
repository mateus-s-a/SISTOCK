from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views import View
from django.views.decorators.cache import cache_page
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.db.models import Q
from django.utils.decorators import method_decorator

from .models import Supplier
from .forms import SupplierForm
from .filters import SupplierFilter

from apps.accounts.mixins import AdminRequiredMixin, ManagerOrAdminRequiredMixin
from django_ratelimit.decorators import ratelimit

# Create your views here.

# --- Views de Fornecedores --- #
class SupplierListView(LoginRequiredMixin, ListView):
    """Lista Fornecedores"""
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 15

    def get_queryset(self):
        """ Adiciona busca simples por nome, email ou CNPJ """
        
        # queryset = super().get_queryset().order_by('name')
        queryset = Supplier.objects.only(
            'id', 'name', 'contact_person', 'email', 'phone'
        ).order_by('name')

        self.filter = SupplierFilter(self.request.GET, queryset=queryset)
        return self.filter.qs
    
    def get_context_data(self, **kwargs):
        """ Adiciona o objeto de filtro ao contexto """
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        context['page_sizes'] = [15, 30, 50]
        context['current_page_size'] = int(self.request.GET.get('page_size', 15))
        return context
    
    def get_paginate_by(self, queryset):
        return self.request.GET.get('page_size', self.paginate_by)



class SupplierDetailView(LoginRequiredMixin, DetailView):
    """Detalhe Fornecedor"""
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'

@method_decorator(ratelimit(key='ip', rate='30/m', method='GET'), name='dispatch')  # Rate limiting para prevenir abuso API
@method_decorator(cache_page(60 * 5), name='dispatch')      # Cache de 5 minutos
class SupplierAutocompleteView(View):
    """
    API endpoint para autocomplete de fornecedores
    API com rate limit: máximo 30 requisições por minuto por IP.
    Cache: 5 minutos para reduzir carga no DB.
    """

    def get(self, request):
        query = request.GET.get('q', '').strip()

        if len(query) < 2:
            return JsonResponse({'results': []})
        
        suppliers = Supplier.objects.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(cnpj__icontains=query)
        ).only('id', 'name', 'email', 'phone').order_by('name')[:10]

        results = [
            {
                'id': s.id,
                'name': s.name,
                'email': s.email,
                'phone': s.phone,
                'url': f'/suppliers/{s.id}/'
            }
            for s in suppliers
        ]
        
        return JsonResponse({
            'results': results,
            'count': len(results),
            'query': query
        })



class SupplierCreateView(ManagerOrAdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Criação Fornecedor"""
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'  # Template reutilizável
    success_url = reverse_lazy('suppliers:supplier_list')
    success_message = 'Fornecedor criado com sucesso.'
    # template_name = 'suppliers/supplier_create.html'

    def get_context_data(self, **kwargs):
        """ Adiciona um título dinâmico para o template do formulário. """
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Criar Fornecedor'
        return context



class SupplierUpdateView(ManagerOrAdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edição Fornecedor"""
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'  # Template reutilizável
    success_url = reverse_lazy('suppliers:supplier_list')
    success_message = 'Fornecedor atualizado com sucesso.'
    # template_name = 'suppliers/supplier_update.html'

    def get_context_data(self, **kwargs):
        """ Adiciona um título dinâmico para o template do formulário. """
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Editar Fornecedor'
        return context


class SupplierDeleteView(AdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Exclusão Fornecedor"""
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list')
    success_message = 'Fornecedor excluído com sucesso.'
    # template_name = 'suppliers/supplier_delete.html'
