from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Product, Category

# Create your views here.

class ProductListView(LoginRequiredMixin, TemplateView):
    """Lista Produtos"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        qs = Product.objects.select_related('category').all().order_by('name')
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(sku__icontains=q)
        return qs
    


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
