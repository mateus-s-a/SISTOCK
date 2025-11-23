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
        def _wrapped_view(request, *args, **kwargs):
            # Usuário não autenticado
            if not request.user.is_authenticated:
                messages.error(request, 'Você precisa estar autenticado.')
                return redirect('login')
            
            # Superuser sempre tem acesso
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verifica role
            if hasattr(request.user, 'profile'):
                if request.user.profile.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
            
            # Sem permissão
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect(redirect_url)
        
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Apenas Admins"""
    return role_required(['ADMIN'])(view_func)


def manager_or_admin_required(view_func):
    """Managers e Admins"""
    return role_required(['ADMIN', 'MANAGER'])(view_func)


def staff_or_above_required(view_func):
    """Todos autenticados"""
    return role_required(['ADMIN', 'MANAGER', 'STAFF'])(view_func)
