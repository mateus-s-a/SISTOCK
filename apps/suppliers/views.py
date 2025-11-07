from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from .models import Supplier
from .forms import SupplierForm
from .filters import SupplierFilter


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
        queryset = super().get_queryset().order_by('name')
        self.filter = SupplierFilter(self.request.GET, queryset=queryset)
        return self.filter.qs
    
    def get_context_data(self, **kwargs):
        """ Adiciona o objeto de filtro ao contexto """
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context



class SupplierDetailView(LoginRequiredMixin, DetailView):
    """Detalhe Fornecedor"""
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'



class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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



class SupplierUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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


class SupplierDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Exclusão Fornecedor"""
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list')
    success_message = 'Fornecedor excluído com sucesso.'
    # template_name = 'suppliers/supplier_delete.html'
