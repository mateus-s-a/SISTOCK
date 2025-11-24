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
            if self.user and hasattr(self.user, 'profile'):
                if self.user.profile.role == 'STAFF' and movement_type != StockMovement.IN:
                    self.add_error('movement_type', "Como Operador/Staff, você somente pode registrar movimentações de entrada.")
                    
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
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Limita tipo de movimentação para STAFF
        if self.user and hasattr(self.user, 'profile') and self.user.profile.role == 'STAFF':
            self.fields['movement_type'].choices = [
                (StockMovement.IN, 'Entrada')
            ]
