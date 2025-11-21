from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from functools import wraps


class RoleRequiredMixin(UserPassesTestMixin):
    """
    Mixin que restringe acesso a views baseado no role do usuario.
    
    Uso:
        class MyView(RoleRequiredMixin, ListView):
        allowed_roles = ['ADMIN', 'MANAGER']
        ...
    """
    allowed_roles = []
    redirect_url = reverse_lazy('inventory:dashboard')
    
    def test_func(self):
        """Verifica se o usuario tem um dos roles permitidos"""
        if not self.request.user.is_authenticated:
            return False
        
        # Superuser sempre tem acesso
        if self.request.user.is_superuser:
            return True
        
        # Verifica se o profile existe e se o role esta permitido
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role in self.allowed_roles
        
        return False
    
    def handle_no_permission(self):
        """Mensagem amigavel quando usuario nao tem permissao"""
        messages.error(
            self.request,
            'Voce nao tem permissao para acessar esta pagina.'
        )
        return redirect(self.redirect_url)


class AdminRequiredMixin(RoleRequiredMixin):
    """Apenas Admins podem acessar"""
    allowed_roles = ['ADMIN']

class ManagerOrAdminRequiredMixin(RoleRequiredMixin):
    """Managers e Admins podem acessar"""
    allowed_roles = ['ADMIN', 'MANAGER']

class StaffOrAboveRequiredMixin(RoleRequiredMixin):
    """Todos os roles autenticados podem acessar"""
    allowed_roles = ['ADMIN', 'MANAGER', 'STAFF']


def role_required(allowed_roles=None, redirect_url='inventory:dashboard'):
    """
    Decorator que restringe acesso a function-based views baseado no role
    
    Uso:
        @role_required(['ADMIN', 'MANAGER'])
        def my_view(request):
        ...
    """
    if allowed_roles is None:
        allowed_roles = []
    
    def decorator(view_func):
        @wraps(view_func)
        def _
