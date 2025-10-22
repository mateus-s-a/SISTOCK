from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Create your views here.

class ProductListView(LoginRequiredMixin, TemplateView):
    """Lista Produtos"""
    template_name = 'products/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TESTE-ESTÁTICO-PRODUCTS => (Lista Produtos)
        context['products'] = [
            {'id': 1, 'name': 'Produto A', 'sku': 'PRD001', 'stock': 50, 'price': 25.99},
            {'id': 2, 'name': 'Produto B', 'sku': 'PRD002', 'stock': 30, 'price': 45.50},
            {'id': 3, 'name': 'Produto C', 'sku': 'PRD003', 'stock': 8, 'price': 15.75},
        ]
        return context


class ProductCreateView(LoginRequiredMixin, TemplateView):
    """Cria Produto"""
    template_name = 'products/product_create.html'

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Produto criado com sucesso. (Simulação)')
        return redirect('products:product_list')


class ProductDetailView(LoginRequiredMixin, TemplateView):
    """Detalhe Produto"""
    template_name = 'products/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TESTE-ESTÁTICO-PRODUCTS => (Detalhe Produtos)
        product_id = kwargs.get('pk', 1)
        context['product'] = {
            'id': product_id,
            'name': f'Produto {product_id}',
            'sku': f'PRD00{product_id}',
            'stock': 50,
            'price': 25.99,
            'description': 'Descrição do produto...'
        }

        return context


class ProductUpdateView(LoginRequiredMixin, TemplateView):
    """Edição Produto"""
    template_name = 'products/product_update.html'

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Produto atualizado com sucesso. (Simulação)')
        return redirect('products:product_list')


class ProductDeleteView(LoginRequiredMixin, TemplateView):
    """Exclusão Produto"""
    template_name = 'products/product_delete.html'

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Produto excluído com sucesso. (Simulação)')
        return redirect('products:product_list')


class CategoryListView(LoginRequiredMixin, TemplateView):
    """Lista Categorias"""
    template_name = 'products/category_list.html'


class CategoryCreateView(LoginRequiredMixin, TemplateView):
    """Criação Categoria"""
    template_name = 'products/category_create.html'
