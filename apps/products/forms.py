from django import forms
from django.forms import widgets
from .models import Category, Product
from django_select2.forms import ModelSelect2Widget

class CategoryForm(forms.ModelForm):
    """
    Formulário para criar e editar Categorias.
    """
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CategoryWidget(ModelSelect2Widget):
    search_fields = [
        'name__icontains',
        'description__icontains',
    ]


class ProductForm(forms.ModelForm):
    """
    Formulário para criar e editar Produtos com validações customizados.
    """
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'category': CategoryWidget(
                attrs={'data-placeholder': 'Digite para buscar uma categoria...'}
            ),
        }
    
    def clean_sku(self):
        """
        Valida se o SKU já existe no BD, desconsiderando o
        próprio objeto em caso de edição.
        """
        sku = self.cleaned_data.get('sku')
        query = Product.objects.filter(sku__iexact=sku)

        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise forms.ValidationError("Já existe um produto com este SKU.")
        return sku

    def clean_stock_quantity(self):
        """
        Valida se a quantidade de estoque é um número não negativo.
        """
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity < 0:
            raise forms.ValidationError("A quantidade em estoque não pode ser negativa.")
        return stock_quantity

    def clean_minimum_stock(self):
        """
        Valida se o estoque mínimo é um número não negativo.
        """
        minimum_stock = self.cleaned_data.get('minimum_stock')
        if minimum_stock < 0:
            raise forms.ValidationError("O estoque mínimo não pode ser negativo.")
        return minimum_stock
        