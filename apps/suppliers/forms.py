import re
from django import forms
from .models import Supplier

class SupplierForm(forms.ModelForm):
    """
    Formulário para criar e editar Fornecedores com validações para
    campos específicos como CNPJ e email.
    """
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'cnpj']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_cnpj(self):
        """
        Valida o formato e a unicidade do CNPJ.
        Remove caracteres não numéricos e verifica se o CNPJ já existe.
        """
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            # Remove caracteres não numéricos
            cnpj_digits = re.sub(r'\D', '', cnpj)

            if len(cnpj_digits) != 14:
                raise forms.ValidationError("CNPJ deve conter 14 dígitos.")
            
            # Verifica unicidade
            query = Supplier.objects.filter(cnpj=cnpj)
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise forms.ValidationError("CNPJ já cadastrado.")
            
            return cnpj
        return cnpj
    
    def clean_email(self):
        """
        Valida se o email já existe em uso por outro fornecedor.
        """
        email = self.cleaned_data.get('email')
        if email:
            query = Supplier.objects.filter(email__iexact=email)
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise forms.ValidationError("Email já cadastrado.")
            
            return email
        return email
        