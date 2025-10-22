from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Create your views here.

class SupplierListView(LoginRequiredMixin, TemplateView):
    """Lista Fornecedores"""
    template_name = 'suppliers/supplier_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TESTE-ESTÁTICO-SUPPLIER => (Lista Fornecedores)
        context['suppliers'] = [
            {'id': 1, 'name': 'Fornecedor A', 'email': 'contato@fornecedora.com', 'phone': '(11) 99999-9999'},
            {'id': 2, 'name': 'Fornecedor B', 'email': 'vendas@fornecedorb.com', 'phone': '(11) 88888-8888'},
        ]
        return context


class SupplierCreateView(LoginRequiredMixin, TemplateView):
    """Criação Fornecedor"""
    template_name = 'suppliers/supplier_create.html'

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Fornecedor criado com sucesso. (Simulação)')
        return redirect('suppliers:supplier_list')


class SupplierDetailView(LoginRequiredMixin, TemplateView):
    """Detalhe Fornecedor"""
    template_name = 'suppliers/supplier_detail.html'


class SupplierUpdateView(LoginRequiredMixin, TemplateView):
    """Edição Fornecedor"""
    template_name = 'suppliers/supplier_update.html'


class SupplierDeleteView(LoginRequiredMixin, TemplateView):
    """Exclusão Fornecedor"""
    template_name = 'suppliers/supplier_delete.html'
