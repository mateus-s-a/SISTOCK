from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from apps.accounts.mixins import AdminRequiredMixin
from .forms import UserRegistrationForm


# Create your views here.

class ProfileView(LoginRequiredMixin, TemplateView):
    """Perfil do Usuário"""
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    

class RegisterView(TemplateView):
    """Registro de Usuário"""
    template_name = 'accounts/register.html'

    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}.')
            return redirect('accounts:login')
        return render(request, self.template_name, {'form': form})
    

class UserRegisterView(AdminRequiredMixin, LoginRequiredMixin, CreateView):
    """
    View para registro de novos usuários.
    Restrita apenas para usuários com role ADMIN.
    """
    form_class = UserRegistrationForm
    template_name = 'accounts/user_register.html'
    success_url = reverse_lazy('accounts:user_register')

    def form_valid(self, form):
        """
        Chamado quando o formulário é válido.
        Adiciona mensagem de sucesso.
        """
        response = super().form_valid(form)
        username = form.cleaned_data['username']
        role = form.cleaned_data['role']
        
        messages.success(
            self.request,
            f'Usuário "{username}" criado com sucesso como {dict(form.fields["role"].choices)[role]}!'
        )
        
        return response

    def form_invalid(self, form):
        """
        Chamado quando o formulário tem erros.
        Adiciona mensagem de erro.
        """
        messages.error(
            self.request,
            'Erro ao criar usuário. Verifique os campos e tente novamente.'
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Adiciona título ao contexto"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Novo Usuário'
        context['subtitle'] = 'Preencha os dados do novo usuário e selecione o papel apropriado'
        return context
