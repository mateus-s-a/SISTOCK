from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile


class UserRegistrationForm(forms.ModelForm):
    """
    Formulário para registro de novos usuários por ADMIN.
    Inclui validação de senha e seleção de role.
    """
    
    # Campos de senha
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha'
        }),
        help_text='Mínimo 8 caracteres'
    )
    
    password2 = forms.CharField(
        label='Confirme a Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha novamente'
        })
    )
    
    # Campo de role (papel)
    role = forms.ChoiceField(
        label='Papel do Usuário',
        choices=Profile.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Define o nível de acesso do usuário no sistema'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário (login)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
        }
        help_texts = {
            'username': 'Obrigatório. 150 caracteres ou menos. Apenas letras, números e @/./+/-/_',
        }

    def clean_username(self):
        """Valida se o username já existe"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nome de usuário já está em uso.')
        return username

    def clean_email(self):
        """Valida se o email já existe"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Este email já está cadastrado.')
        return email

    def clean_password2(self):
        """Valida se as senhas conferem"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('As senhas não conferem.')
            
            # Validação de tamanho mínimo
            if len(password1) < 8:
                raise ValidationError('A senha deve ter no mínimo 8 caracteres.')
        
        return password2

    def save(self, commit=True):
        """
        Salva o usuário com senha hasheada e atribui o role ao Profile.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
            
            # O Profile já foi criado pelo signal, só atualizamos o role
            role = self.cleaned_data['role']
            user.profile.role = role
            user.profile.save()  # Isso vai acionar o signal para atribuir o Group
            
        return user
