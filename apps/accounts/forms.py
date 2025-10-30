from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# Futuramente, importar o modelo de usuário customizado
# from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # model = CustomUser  # Descomente quando o modelo customizado estiver disponível
        fields = ('username', 'email')  # Adicione outros campos conforme necessário

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        # model = CustomUser  # Descomente quando o modelo customizado estiver disponível
        fields = ('username', 'email')  # Adicione outros campos conforme necessário
