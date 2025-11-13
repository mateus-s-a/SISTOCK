"""
Management command para popular a tabela StockMovement com dados de teste.
Uso: python manage.py create_movements [opções]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
from apps.inventory.models import StockMovement
from apps.products.models import Product
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    """
    Comando para criar movimentações de estoque usando Faker.
    """
    
    help = 'Popula a tabela StockMovement com movimentações de teste e atualiza estoques'
    
    # Razões para cada tipo de movimentação
    REASONS = {
        'IN': [
            'Compra de fornecedor',
            'Devolução de cliente',
            'Transferência entre unidades',
            'Produção interna',
            'Correção de inventário - entrada',
            'Retorno de conserto',
            'Recebimento de doação',
        ],
        'OUT': [
            'Venda ao cliente',
            'Devolução ao fornecedor',
            'Perda/Avaria',
            'Quebra durante manuseio',
            'Amostra grátis',
            'Uso interno',
            'Correção de inventário - saída',
            'Vencimento de validade',
        ],
        'ADJ': [
            'Ajuste de inventário',
            'Correção de lançamento',
            'Auditoria de estoque',
            'Reconciliação de sistema',
            'Ajuste por divergência',
        ]
    }
    
    def add_arguments(self, parser):
        """
        Define argumentos aceitos pelo comando.
        """
        parser.add_argument(
            '--quantity',
            type=int,
            default=200,
            help='Quantidade de movimentações a criar (padrão: 200)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todas as movimentações e reseta estoques'
        )
        
        parser.add_argument(
            '--seed',
            type=int,
            default=None,
            help='Seed para gerar dados reproduzíveis'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Número de dias no passado para distribuir movimentações (padrão: 90)'
        )
        
        parser.add_argument(
            '--update-stock',
            action='store_true',
            default=True,
            help='Atualiza estoque dos produtos (padrão: True)'
        )
    
    def generate_movement_date(self, fake, days):
        """
        Gera uma data nos últimos N dias.
        """
        start_date = timezone.now() - timedelta(days=days)
        end_date = timezone.now()
        return fake.date_time_between(start_date=start_date, end_date=end_date, tzinfo=timezone.get_current_timezone())
    
    def generate_quantity(self, fake, movement_type):
        """
        Gera quantidade apropriada para o tipo de movimentação.
        """
        if movement_type == 'IN':
            # Entradas: geralmente maiores (10-200)
            return fake.random_int(min=10, max=200)
        elif movement_type == 'OUT':
            # Saídas: geralmente menores (1-50)
            return fake.random_int(min=1, max=50)
        else:  # ADJ
            # Ajustes: podem ser positivos ou negativos, pequenos (-20 a +20)
            adjustment = fake.random_int(min=-20, max=20)
            return adjustment if adjustment != 0 else 1
    
    def update_product_stock(self, product, movement_type, quantity):
        """
        Atualiza o estoque do produto baseado na movimentação.
        """
        if movement_type == 'IN':
            product.stock_quantity += quantity
        elif movement_type == 'OUT':
            product.stock_quantity = max(0, product.stock_quantity - quantity)
        else:  # ADJ
            if quantity > 0:
                product.stock_quantity += quantity
            else:
                product.stock_quantity = max(0, product.stock_quantity + quantity)
        
        product.save(update_fields=['stock_quantity'])
    
    def handle(self, *args, **options):
        """
        Lógica principal do comando.
        """
        quantity = options['quantity']
        clear = options['clear']
        seed = options['seed']
        days = options['days']
        update_stock = options['update_stock']
        
        # Validações
        if quantity < 1:
            self.stdout.write(
                self.style.ERROR('❌ Quantidade deve ser maior que 0')
            )
            return
        
        if quantity > 10000:
            self.stdout.write(
                self.style.ERROR('❌ Quantidade máxima: 10000 movimentações')
            )
            return
        
        # Verificar pré-requisitos
        products_count = Product.objects.count()
        if products_count == 0:
            self.stdout.write(
                self.style.ERROR(
                    '\n❌ Nenhum produto encontrado!\n'
                    'Crie produtos antes de gerar movimentações:\n'
                    '  $ python manage.py create_products\n'
                )
            )
            return
        
        users_count = User.objects.count()
        if users_count == 0:
            self.stdout.write(
                self.style.ERROR(
                    '\n❌ Nenhum usuário encontrado!\n'
                    'Crie um superusuário antes:\n'
                    '  $ python manage.py createsuperuser\n'
                )
            )
            return
        
        # Inicializar Faker
        fake = Faker('pt_BR')
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)
            self.stdout.write(f'🌱 Usando seed: {seed}')
        
        # Limpar dados se solicitado
        if clear:
            self.stdout.write('🗑️  Removendo movimentações existentes...')
            movements_count = StockMovement.objects.count()
            
            if movements_count > 0:
                StockMovement.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(f'   ✅ Removidas {movements_count} movimentações')
                )
                
                # Resetar estoques para valores aleatórios
                if update_stock:
                    self.stdout.write('   🔄 Resetando estoques dos produtos...')
                    for product in Product.objects.all():
                        product.stock_quantity = fake.random_int(min=0, max=100)
                        product.save(update_fields=['stock_quantity'])
                    self.stdout.write(
                        self.style.SUCCESS('   ✅ Estoques resetados\n')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING('   Nenhuma movimentação para remover.\n')
                )
        
        # Buscar produtos e usuários
        products = list(Product.objects.all())
        users = list(User.objects.all())
        
        # Distribuição de tipos de movimentação (mais realista)
        # 40% entradas, 45% saídas, 15% ajustes
        movement_types_distribution = (
            ['IN'] * 40 + 
            ['OUT'] * 45 + 
            ['ADJ'] * 15
        )
        
        self.stdout.write(
            f'📦 Gerando {quantity} movimentações para {products_count} produtos...\n'
        )
        
        movements_list = []
        created_count = 0
        movement_stats = {'IN': 0, 'OUT': 0, 'ADJ': 0}
        
        for i in range(quantity):
            # Selecionar tipo de movimentação
            movement_type = fake.random_element(movement_types_distribution)
            
            # Selecionar produto e usuário aleatórios
            product = fake.random_element(products)
            user = fake.random_element(users)
            
            # Gerar quantidade
            quantity_value = self.generate_quantity(fake, movement_type)
            
            # Para ajustes negativos, garantir que é negativo
            if movement_type == 'ADJ' and quantity_value < 0:
                quantity_value = abs(quantity_value) * -1
            
            # Gerar razão
            reason = fake.random_element(self.REASONS[movement_type])
            
            # Gerar data
            created_at = self.generate_movement_date(fake, days)
            
            # Criar objeto StockMovement
            movement = StockMovement(
                product=product,
                movement_type=movement_type,
                quantity=abs(quantity_value),  # Django espera positivo
                reason=reason,
                user=user,
                created_at=created_at
            )
            movements_list.append(movement)
            
            # Atualizar estoque se solicitado
            if update_stock:
                self.update_product_stock(product, movement_type, quantity_value)
            
            movement_stats[movement_type] += 1
            created_count += 1
            
            # Feedback visual a cada 50 movimentações
            if (i + 1) % 50 == 0:
                self.stdout.write(f'   ⏳ Processando... {i + 1}/{quantity}')
        
        # Salvar no banco usando bulk_create
        if movements_list:
            try:
                with transaction.atomic():
                    StockMovement.objects.bulk_create(
                        movements_list,
                        batch_size=100
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\n✅ {created_count} movimentações criadas com sucesso!\n'
                        )
                    )
                    
                    # Mostrar amostra
                    self.stdout.write('📋 Amostra das movimentações criadas:')
                    for i, movement in enumerate(movements_list[:5], 1):
                        type_emoji = {'IN': '📥', 'OUT': '📤', 'ADJ': '🔧'}
                        self.stdout.write(
                            f'   {i}. {type_emoji[movement.movement_type]} '
                            f'{movement.get_movement_type_display()} | '
                            f'{movement.product.name} | '
                            f'Qtd: {movement.quantity} | '
                            f'{movement.reason}'
                        )
                    
                    if len(movements_list) > 5:
                        self.stdout.write(f'   ... e mais {len(movements_list) - 5} movimentações')
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ Erro ao criar movimentações: {str(e)}')
                )
                return
        
        # Estatísticas finais
        total_movements = StockMovement.objects.count()
        low_stock = Product.objects.filter(
            stock_quantity__lte=F('minimum_stock')
        ).count()
        out_of_stock = Product.objects.filter(stock_quantity=0).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 ESTATÍSTICAS:\n'
                f'   Total de movimentações: {total_movements}\n'
                f'   📥 Entradas: {movement_stats["IN"]}\n'
                f'   📤 Saídas: {movement_stats["OUT"]}\n'
                f'   🔧 Ajustes: {movement_stats["ADJ"]}\n\n'
                f'   🏭 STATUS DOS PRODUTOS:\n'
                f'   🔴 Estoque baixo: {low_stock}\n'
                f'   ⚫ Sem estoque: {out_of_stock}\n'
            )
        )
