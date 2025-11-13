"""
Management command MASTER para popular todo o banco de dados.
Executa todos os comandos de população em sequência.
Uso: python manage.py create_all_data [opções]
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
import time

User = get_user_model()


class Command(BaseCommand):
    """
    Comando master que executa todos os comandos de população.
    """
    
    help = 'Popula todo o banco de dados com dados de teste (categorias, produtos, fornecedores e movimentações)'
    
    # Presets de quantidade por tamanho
    PRESETS = {
        'small': {
            'categories': 10,
            'products': 30,
            'suppliers': 15,
            'movements': 100,
        },
        'medium': {
            'categories': 15,
            'products': 100,
            'suppliers': 30,
            'movements': 300,
        },
        'large': {
            'categories': 25,
            'products': 500,
            'suppliers': 50,
            'movements': 1000,
        }
    }
    
    def add_arguments(self, parser):
        """
        Define argumentos aceitos pelo comando.
        """
        parser.add_argument(
            '--size',
            type=str,
            choices=['small', 'medium', 'large'],
            default='medium',
            help='Tamanho do dataset: small, medium ou large (padrão: medium)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa todos os dados antes de popular'
        )
        
        parser.add_argument(
            '--seed',
            type=int,
            default=None,
            help='Seed para gerar dados reproduzíveis'
        )
        
        parser.add_argument(
            '--skip-categories',
            action='store_true',
            help='Pula criação de categorias'
        )
        
        parser.add_argument(
            '--skip-products',
            action='store_true',
            help='Pula criação de produtos'
        )
        
        parser.add_argument(
            '--skip-suppliers',
            action='store_true',
            help='Pula criação de fornecedores'
        )
        
        parser.add_argument(
            '--skip-movements',
            action='store_true',
            help='Pula criação de movimentações'
        )
        
        parser.add_argument(
            '--create-user',
            action='store_true',
            help='Cria um usuário admin padrão se não existir'
        )
    
    def print_banner(self):
        """
        Imprime banner inicial.
        """
        banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🏭 SISTOCK - POPULATION MASTER 🏭              ║
║                                                          ║
║        Populando banco de dados com dados de teste       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """
        self.stdout.write(self.style.SUCCESS(banner))
    
    def print_step(self, step_number, total_steps, title):
        """
        Imprime cabeçalho de cada etapa.
        """
        self.stdout.write(
            self.style.HTTP_INFO(
                f'\n{"="*60}\n'
                f'  ETAPA {step_number}/{total_steps}: {title}\n'
                f'{"="*60}\n'
            )
        )
    
    def create_default_user(self):
        """
        Cria um usuário admin padrão se não existir.
        """
        if User.objects.filter(username='admin').exists():
            self.stdout.write(
                self.style.WARNING('   ⚠️  Usuário "admin" já existe. Pulando...')
            )
            return
        
        try:
            user = User.objects.create_superuser(
                username='admin',
                email='admin@sistock.local',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'   ✅ Usuário admin criado!\n'
                    f'   Username: admin\n'
                    f'   Password: admin123\n'
                    f'   ⚠️  ALTERE A SENHA EM PRODUÇÃO!\n'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro ao criar usuário: {str(e)}')
            )
    
    def handle(self, *args, **options):
        """
        Lógica principal do comando.
        """
        size = options['size']
        clear = options['clear']
        seed = options['seed']
        create_user = options['create_user']
        
        skip_categories = options['skip_categories']
        skip_products = options['skip_products']
        skip_suppliers = options['skip_suppliers']
        skip_movements = options['skip_movements']
        
        # Obter configurações do preset
        config = self.PRESETS[size]
        
        # Banner inicial
        self.print_banner()
        
        # Informações do processo
        self.stdout.write(
            self.style.WARNING(
                f'\n📊 CONFIGURAÇÃO:\n'
                f'   Tamanho: {size.upper()}\n'
                f'   Categorias: {config["categories"]}\n'
                f'   Produtos: {config["products"]}\n'
                f'   Fornecedores: {config["suppliers"]}\n'
                f'   Movimentações: {config["movements"]}\n'
                f'   Limpar dados: {"Sim" if clear else "Não"}\n'
                f'   Seed: {seed if seed else "Aleatório"}\n'
            )
        )
        
        # Calcular número total de etapas
        total_steps = sum([
            not skip_categories,
            not skip_products,
            not skip_suppliers,
            not skip_movements,
            create_user
        ])
        
        current_step = 0
        start_time = time.time()
        
        # Etapa 0: Criar usuário se solicitado
        if create_user:
            current_step += 1
            self.print_step(current_step, total_steps, 'CRIAR USUÁRIO ADMIN')
            self.create_default_user()
        
        # Verificar se usuário existe (necessário para movimentações)
        if not skip_movements:
            if User.objects.count() == 0 and not create_user:
                self.stdout.write(
                    self.style.ERROR(
                        '\n❌ ERRO: Nenhum usuário encontrado!\n'
                        'Movimentações requerem um usuário.\n'
                        'Execute com --create-user ou crie um superusuário:\n'
                        '  $ python manage.py createsuperuser\n'
                    )
                )
                return
        
        # Preparar argumentos comuns
        common_args = {'verbosity': 1}
        if seed is not None:
            common_args['seed'] = seed
        
        # Etapa 1: Categorias
        if not skip_categories:
            current_step += 1
            self.print_step(current_step, total_steps, 'CATEGORIAS')
            try:
                call_command(
                    'create_categories',
                    quantity=config['categories'],
                    clear=clear,
                    **common_args
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao criar categorias: {str(e)}')
                )
                return
        
        # Etapa 2: Produtos
        if not skip_products:
            current_step += 1
            self.print_step(current_step, total_steps, 'PRODUTOS')
            
            # Verificar se há categorias
            from apps.products.models import Category
            if Category.objects.count() == 0:
                self.stdout.write(
                    self.style.ERROR(
                        '❌ Nenhuma categoria encontrada!\n'
                        'Execute sem --skip-categories ou crie categorias primeiro.'
                    )
                )
                return
            
            try:
                call_command(
                    'create_products',
                    quantity=config['products'],
                    clear=clear,
                    **common_args
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao criar produtos: {str(e)}')
                )
                return
        
        # Etapa 3: Fornecedores
        if not skip_suppliers:
            current_step += 1
            self.print_step(current_step, total_steps, 'FORNECEDORES')
            try:
                call_command(
                    'create_suppliers',
                    quantity=config['suppliers'],
                    clear=clear,
                    **common_args
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao criar fornecedores: {str(e)}')
                )
                return
        
        # Etapa 4: Movimentações
        if not skip_movements:
            current_step += 1
            self.print_step(current_step, total_steps, 'MOVIMENTAÇÕES DE ESTOQUE')
            
            # Verificar se há produtos
            from apps.products.models import Product
            if Product.objects.count() == 0:
                self.stdout.write(
                    self.style.ERROR(
                        '❌ Nenhum produto encontrado!\n'
                        'Execute sem --skip-products ou crie produtos primeiro.'
                    )
                )
                return
            
            try:
                call_command(
                    'create_movements',
                    quantity=config['movements'],
                    clear=clear,
                    **common_args
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao criar movimentações: {str(e)}')
                )
                return
        
        # Resumo final
        elapsed_time = time.time() - start_time
        
        # Buscar estatísticas finais
        from apps.products.models import Category, Product
        from apps.suppliers.models import Supplier
        from apps.inventory.models import StockMovement
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*60}\n'
                f'  ✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!\n'
                f'{"="*60}\n\n'
                f'📊 ESTATÍSTICAS FINAIS:\n'
                f'   Categorias: {Category.objects.count()}\n'
                f'   Produtos: {Product.objects.count()}\n'
                f'   Fornecedores: {Supplier.objects.count()}\n'
                f'   Movimentações: {StockMovement.objects.count()}\n'
                f'   Usuários: {User.objects.count()}\n\n'
                f'⏱️  Tempo total: {elapsed_time:.2f} segundos\n\n'
                f'🚀 O banco de dados está pronto para uso!\n'
            )
        )
