from django import forms
from .models import StockMovement, Product

class StockMovementForm(forms.ModelForm):
    """
    Formulário para registrar movimentações de estoque com validação
    para não permitir estoque negativo
    """
    
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'reason']
    
    def clean(self):
        """
        Validação customizada para o formulário inteiro
        """
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        quantity = cleaned_data.get('quantity')
        product = cleaned_data.get('product')

        if not all([movement_type, quantity, product]):
            return cleaned_data  # Campos obrigatórios não preenchidos
        

        # Regra 1: Saída devem ter quantidade positiva
        if movement_type == StockMovement.OUT and quantity <= 0:
            self.add_error('quantity', "Para saídas, a quantidade deve ser positiva.")
        
        # Regra 2: Entradas devem ter quantidade positiva
        if movement_type == StockMovement.IN and quantity <= 0:
            self.add_error('quantity', "Para entradas, a quantidade deve ser positiva.")
        
        # Regra 3: Não permitir que uma saída deixe o estoque negativo
        if movement_type == StockMovement.OUT:
            if product.stock_quantity < quantity:
                self.add_error('quantity', f"Estoque insuficiente. Quantidade disponível: {product.stock_quantity}.")
