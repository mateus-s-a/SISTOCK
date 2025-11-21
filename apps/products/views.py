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

from .models import Product, Category
from .forms import ProductForm, CategoryForm
from .filters import ProductFilter


# Create your views here.

# --- Views de Produto --- #
class ProductListView(LoginRequiredMixin, ListView):
    """Lista Produtos"""
    model = Product
    template_name = 'products/product_list.html'
    success_url = reverse_lazy('products:product_list')
    context_object_name = 'products'
    paginate_by = 15

    def get_queryset(self):
        """Adiciona busca simples ao queryset"""
        
        # queryset = super().get_queryset().select_related('category').order_by('name')

        queryset = Product.objects.select_related('category').only(
            'id', 'name', 'sku', 'price', 'stock_quantity', 'minimum_stock',
            'category__name'
        ).order_by('name')
        
        self.filter = ProductFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        """
        Adiciona o objeto de filtro ao contexto para ser usado no template
        """
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter

        # Adiciona opções de paginação personalizável
        context['page_sizes'] = [15, 30, 50, 100]
        context['current_page_size'] = int(self.request.GET.get('page_size', 15))

        return context
    
    def get_paginate_by(self, queryset):
        """
        Permite ao usuário escolher quantos itens ver por página
        """
        return self.request.GET.get('page_size', self.paginate_by)
    

class ProductDetailView(LoginRequiredMixin, DetailView):
    """Detalhe Produto"""
    model = Product
    template_name = 'products/product_detail.html'
    success_url = reverse_lazy('products:product_detail')
    context_object_name = 'product'



class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Cria Produto"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'    # Template reutilizável
    success_url = reverse_lazy('products:product_list')
    success_message = 'Produto criado com sucesso.'
    # template_name = 'products/product_create.html'

    def get_context_data(self, **kwargs):
        """Adiciona título ao contexto"""
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Criar Produto'
        return context



class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edição Produto"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'    # Template reutilizável
    success_url = reverse_lazy('products:product_list')
    success_message = 'Produto atualizado com sucesso.'
    # template_name = 'products/product_update.html'

    def get_context_data(self, **kwargs):
        """Adiciona título ao contexto"""
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Editar Produto'
        return context
    


class ProductDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Exclusão Produto"""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    success_message = 'Produto excluído com sucesso.'
    # template_name = 'products/product_delete.html'



# --- Views de Categoria --- #

class CategoryListView(LoginRequiredMixin, ListView):
    """Lista Categorias"""
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    paginate_by = 15


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Criação Categoria"""
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'    # Template reutilizável
    success_url = reverse_lazy('products:category_list')
    success_message = 'Categoria criada com sucesso.'
    # template_name = 'products/category_create.html'
