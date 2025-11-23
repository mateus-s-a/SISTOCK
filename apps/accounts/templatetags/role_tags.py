from django import template

register = template.Library()

@register.filter
def has_role(user, roles):
    """
    Verifica se o usuário tem um dos roles especificados.
    
    Uso no template:
        {% if request.user|has_role:"ADMIN,MANAGER" %}
            <button>Editar</button>
        {% endif %}
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    if hasattr(user, 'profile'):
        allowed_roles = [r.strip() for r in roles.split(',')]
        return user.profile.role in allowed_roles
    
    return False


@register.simple_tag
def user_role(user):
    """
    Retorna o role do usuário.
    
    Uso:
        {% user_role request.user as role %}
        Você está logado como: {{ role }}
    """
    if hasattr(user, 'profile'):
        return user.profile.get_role_display()
    return 'Sem perfil'
