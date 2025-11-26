import logging

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

from .models import Product, Category
from .forms import ProductForm, CategoryForm
from .filters import ProductFilter

from apps.accounts.mixins import AdminRequiredMixin, ManagerOrAdminRequiredMixin, admin_required
from django_ratelimit.decorators import ratelimit


logger = logging.getLogger(__name__)


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



@method_decorator(ratelimit(key='ip', rate='30/m', method='GET'), name='dispatch')  # Rate limiting para prevenir abuso API
@method_decorator(cache_page(60 * 5), name='dispatch')      # Cache de 5 minutos
class ProductAutocompleteView(View):
    """
    API endpoint para autocomplete de produtos.
    API com rate limit: máximo 30 requisições por minuto por IP.
    Retorna JSON com produtos que correspondem ao termo de busca.
    Cache: 5 minutos para reduzir carga no DB.
    """

    def get(self, request):
        # Pega o termo de busca
        query = request.GET.get('q', '').strip()

        # Retorna vazio se query for muito curta
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        logger.info(f"Autocomplete search: query='{query}' ip={request.META.get('REMOTE_ADDR')}")
        
        # Busca produtos (case-insensitive, busca parcial)
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(description__icontains=query)
        ).select_related('category').only(
            'id', 'name', 'sku', 'stock_quantity', 'price', 'category__name'
        ).order_by('name')[:10]  # Limita a 10 resultados

        # Formata resultados como JSON
        results = [
            {
                'id': p.id,
                'name': p.name,
                'sku': p.sku,
                'category': p.category.name if p.category else 'Sem categoria',
                'stock': p.stock_quantity,
                'price': float(p.price),
                'url': f'/products/{p.id}/',  # URL para detalhes
            }
            for p in products
        ]

        return JsonResponse({
            'results': results,
            'count': len(results),
            'query': query
        })



class ProductCreateView(ManagerOrAdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, CreateView):
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



class ProductUpdateView(ManagerOrAdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edição Produto - MANAGER ou ADMIN"""
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
    


class ProductDeleteView(AdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Exclusão Produto - apenas ADMIN"""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    success_message = 'Produto excluído com sucesso.'
    # template_name = 'products/product_delete.html'

    # @admin_required
    # def delete_all_products(request):
    #     Product.objects.all().delete()
    #     messages.success(request, 'Todos os produtos foram removidos.')
    #     return redirect('products:product_list')



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

