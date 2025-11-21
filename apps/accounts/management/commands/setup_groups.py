from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.products.models import Product, Category
from apps.suppliers.models import Supplier
from apps.inventory.models import StockMovement


class Command(BaseCommand):
    help = 'Configura grupos de usuários com permissões padrão'

    def handle(self, *args, **kwargs):
        # Limpa grupos existentes (opcional, só use em dev/setup inicial)
        Group.objects.filter(name__in=['Admin', 'Manager', 'Staff']).delete()
        
        # Cria grupos
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        staff_group, _ = Group.objects.get_or_create(name='Staff')


        # ========== PERMISSÕES PARA ADMIN (TODAS) ==========
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)


        # ========== PERMISSÕES PARA MANAGER ==========
        manager_permissions = []
        
        # Produtos: adicionar, modificar, visualizar (sem deletar)
        product_ct = ContentType.objects.get_for_model(Product)
        manager_permissions.extend([
            Permission.objects.get(codename='add_product', content_type=product_ct),
            Permission.objects.get(codename='change_product', content_type=product_ct),
            Permission.objects.get(codename='view_product', content_type=product_ct),
        ])
        
        # Categorias: adicionar, modificar, visualizar (sem deletar)
        category_ct = ContentType.objects.get_for_model(Category)
        manager_permissions.extend([
            Permission.objects.get(codename='add_category', content_type=category_ct),
            Permission.objects.get(codename='change_category', content_type=category_ct),
            Permission.objects.get(codename='view_category', content_type=category_ct),
        ])
        
        # Fornecedores: adicionar, modificar, visualizar (sem deletar)
        supplier_ct = ContentType.objects.get_for_model(Supplier)
        manager_permissions.extend([
            Permission.objects.get(codename='add_supplier', content_type=supplier_ct),
            Permission.objects.get(codename='change_supplier', content_type=supplier_ct),
            Permission.objects.get(codename='view_supplier', content_type=supplier_ct),
        ])
        
        # Movimentações: todas as permissões
        movement_ct = ContentType.objects.get_for_model(StockMovement)
        manager_permissions.extend([
            Permission.objects.get(codename='add_stockmovement', content_type=movement_ct),
            Permission.objects.get(codename='change_stockmovement', content_type=movement_ct),
            Permission.objects.get(codename='view_stockmovement', content_type=movement_ct),
            Permission.objects.get(codename='delete_stockmovement', content_type=movement_ct),
        ])
        
        manager_group.permissions.set(manager_permissions)


        # ========== PERMISSÕES PARA STAFF ==========
        staff_permissions = []
        
        # Produtos: apenas visualizar
        staff_permissions.append(
            Permission.objects.get(codename='view_product', content_type=product_ct)
        )
        
        # Categorias: apenas visualizar
        staff_permissions.append(
            Permission.objects.get(codename='view_category', content_type=category_ct)
        )
        
        # Fornecedores: apenas visualizar
        staff_permissions.append(
            Permission.objects.get(codename='view_supplier', content_type=supplier_ct)
        )
        
        # Movimentações: adicionar e visualizar (entrada de estoque)
        staff_permissions.extend([
            Permission.objects.get(codename='add_stockmovement', content_type=movement_ct),
            Permission.objects.get(codename='view_stockmovement', content_type=movement_ct),
        ])
        
        staff_group.permissions.set(staff_permissions)


        self.stdout.write(self.style.SUCCESS('✅ Grupos e permissões configurados com sucesso!'))
        self.stdout.write(self.style.SUCCESS(f'   - Admin: {admin_group.permissions.count()} permissões'))
        self.stdout.write(self.style.SUCCESS(f'   - Manager: {manager_group.permissions.count()} permissões'))
        self.stdout.write(self.style.SUCCESS(f'   - Staff: {staff_group.permissions.count()} permissões'))
