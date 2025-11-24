from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def assign_user_group(sender, instance, **kwargs):
    """
    Atribui automaticaente o grupo do Django baseado no role do perfil
    """
    # Remove usuario de todos os grupos
    instance.user.groups.clear()
    
    # Mapeia role para nome do grupo
    role_to_group = {
        Profile.ADMIN: 'Admin',
        Profile.MANAGER: 'Manager',
        Profile.STAFF: 'Staff',
    }
    
    group_name = role_to_group.get(instance.role)
    if group_name:
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.user.groups.add(group)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
