from django import forms
from .models import Category, Product

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

class ProductForm(forms.ModelForm):
    """
    Formulário para criar e editar Produtos com validações customizados.
    """
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'description',
            'price', 'stock_quantity', 'minimum_stock',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_sku(self):
        """
        Valida se o SKU já existe no BD, desconsiderando o
        próprio objeto em caso de edição.
        """
        sku = self.cleaned_data.get('sku')
        query = Product.objects.filter(sku__iexact=sku)

        if self.isinstance and self.instance.pk:
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
        