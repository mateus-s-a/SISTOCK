"""
Management command para popular a tabela Product com dados de teste.
Uso: python manage.py create_products [opções]
"""

from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.db.models import F
from decimal import Decimal
from faker import Faker
from apps.products.models import Product, Category
import random


class Command(BaseCommand):
    """
    Comando para criar produtos usando Faker.
    """
    
    help = 'Popula a tabela Product com produtos de teste gerados dinamicamente'
    
    # Listas para geração de nomes de produtos
    PRODUCT_ADJECTIVES = [
        'Premium', 'Pro', 'Ultra', 'Master', 'Super', 'Mega', 'Plus',
        'Deluxe', 'Smart', 'Eco', 'Turbo', 'Max', 'Power', 'Compact',
        'Ergonômico', 'Portátil', 'Digital', 'Automático', 'Profissional'
    ]
    
    PRODUCT_TYPES = [
        'Notebook', 'Mouse', 'Teclado', 'Monitor', 'Cadeira', 'Mesa',
        'Fone', 'Webcam', 'Impressora', 'Scanner', 'Projetor', 'Tablet',
        'Smartphone', 'Smartwatch', 'SSD', 'HD Externo', 'Memória RAM',
        'Processador', 'Placa de Vídeo', 'Fonte', 'Gabinete', 'Cooler',
        'Estabilizador', 'Nobreak', 'Roteador', 'Switch', 'Cabo HDMI',
        'Adaptador', 'Carregador', 'Bateria', 'Mousepad', 'Suporte'
    ]
    
    PRODUCT_DESCRIPTORS = [
        'Gamer', 'Office', 'Home', 'Business', 'Studio', 'Wireless',
        'Bluetooth', 'USB', 'RGB', 'LED', 'Full HD', '4K', 'Mecânico',
        'Óptico', 'Laser', 'Silencioso', 'Ajustável', 'Dobrável'
    ]
    
    def add_arguments(self, parser):
        """
        Define argumentos aceitos pelo comando.
        """
        parser.add_argument(
            '--quantity',
            type=int,
            default=50,
            help='Quantidade de produtos a criar (padrão: 50)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todos os produtos existentes antes de criar novos'
        )
        
        parser.add_argument(
            '--seed',
            type=int,
            default=None,
            help='Seed para gerar dados reproduzíveis (opcional)'
        )
        
        parser.add_argument(
            '--min-price',
            type=float,
            default=10.0,
            help='Preço mínimo dos produtos (padrão: 10.00)'
        )
        
        parser.add_argument(
            '--max-price',
            type=float,
            default=5000.0,
            help='Preço máximo dos produtos (padrão: 5000.00)'
        )
        
        parser.add_argument(
            '--low-stock-percent',
            type=int,
            default=20,
            help='Percentual de produtos com estoque baixo (padrão: 20%%)'
        )
    
    def generate_sku(self, fake, used_skus=None):
        """
        Gera um SKU único no formato: ABC123456 (3 letras + 6 números).
        
        Args:
            fake: Instância do Faker
            used_skus: Set com SKUs já utilizados
            
        Returns:
            str: SKU único
        """
        if used_skus is None:
            used_skus = set()
        
        max_attempts = 100
        
        for _ in range(max_attempts):
            # 3 letras maiúsculas + 6 dígitos
            letters = ''.join(fake.random_letters(length=3)).upper()
            numbers = fake.numerify(text='######')
            sku = f"{letters}{numbers}"
            
            if sku not in used_skus:
                used_skus.add(sku)
                return sku
        
        # Fallback: adicionar timestamp
        import time
        timestamp = str(int(time.time()))[-6:]
        letters = ''.join(fake.random_letters(length=3)).upper()
        sku = f"{letters}{timestamp}"
        used_skus.add(sku)
        return sku
    
    def generate_product_name(self, fake):
        """
        Gera um nome de produto realista.
        
        Returns:
            str: Nome do produto
        """
        patterns = [
            # Padrão 1: Tipo + Descritor
            lambda: f"{fake.random_element(self.PRODUCT_TYPES)} {fake.random_element(self.PRODUCT_DESCRIPTORS)}",
            
            # Padrão 2: Adjetivo + Tipo
            lambda: f"{fake.random_element(self.PRODUCT_ADJECTIVES)} {fake.random_element(self.PRODUCT_TYPES)}",
            
            # Padrão 3: Adjetivo + Tipo + Descritor
            lambda: f"{fake.random_element(self.PRODUCT_ADJECTIVES)} {fake.random_element(self.PRODUCT_TYPES)} {fake.random_element(self.PRODUCT_DESCRIPTORS)}",
            
            # Padrão 4: Tipo + Adjetivo
            lambda: f"{fake.random_element(self.PRODUCT_TYPES)} {fake.random_element(self.PRODUCT_ADJECTIVES)}",
            
            # Padrão 5: Tipo simples com modelo
            lambda: f"{fake.random_element(self.PRODUCT_TYPES)} {fake.lexify(text='??-###', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        ]
        
        pattern = fake.random_element(patterns)
        return pattern()
    
    def generate_description(self, fake, product_name):
        """
        Gera uma descrição realista para o produto.
        
        Args:
            fake: Instância do Faker
            product_name: Nome do produto
            
        Returns:
            str: Descrição do produto
        """
        templates = [
            f"{product_name} ideal para uso profissional e doméstico. "
            f"Produto de alta qualidade com garantia do fabricante. "
            f"Compatível com diversos sistemas e fácil de usar.",
            
            f"O {product_name} oferece excelente desempenho e durabilidade. "
            f"Design moderno e funcional. Perfeito para quem busca qualidade.",
            
            f"{product_name} com tecnologia avançada e acabamento premium. "
            f"Ideal para profissionais exigentes. Garantia de 12 meses.",
            
            f"Adquira o {product_name} e aproveite recursos exclusivos. "
            f"Produto certificado e testado. Melhor custo-benefício do mercado.",
            
            f"{product_name} - a escolha inteligente para seu escritório ou casa. "
            f"Alta performance e economia. Entrega rápida e segura.",
        ]
        
        return fake.random_element(templates)
    
    def generate_price(self, fake, min_price, max_price):
        """
        Gera um preço realista terminando em .90, .95 ou .99.
        
        Args:
            fake: Instância do Faker
            min_price: Preço mínimo
            max_price: Preço máximo
            
        Returns:
            Decimal: Preço do produto
        """
        # Gerar valor base
        base_price = fake.random_int(min=int(min_price), max=int(max_price))
        
        # 70% de chance de terminar em .90, .95 ou .99
        if fake.random_int(min=1, max=100) <= 70:
            cents = fake.random_element([90, 95, 99])
        else:
            # 30% de chance de ser valor "quebrado"
            cents = fake.random_int(min=0, max=99)
        
        price = Decimal(f"{base_price}.{cents:02d}")
        return price
    
    def generate_stock_quantity(self, fake, is_low_stock=False):
        """
        Gera quantidade em estoque.
        
        Args:
            fake: Instância do Faker
            is_low_stock: Se True, gera estoque baixo
            
        Returns:
            int: Quantidade em estoque
        """
        if is_low_stock:
            # Estoque baixo: 0 a 10 unidades
            return fake.random_int(min=0, max=10)
        else:
            # Estoque normal: 20 a 500 unidades
            return fake.random_int(min=20, max=500)
    
    def generate_minimum_stock(self, fake):
        """
        Gera quantidade mínima de estoque.
        
        Returns:
            int: Estoque mínimo
        """
        return fake.random_int(min=5, max=50)
    
    def handle(self, *args, **options):
        """
        Lógica principal do comando.
        """
        quantity = options['quantity']
        clear = options['clear']
        seed = options['seed']
        min_price = options['min_price']
        max_price = options['max_price']
        low_stock_percent = options['low_stock_percent']
        
        # Validações
        if quantity < 1:
            self.stdout.write(
                self.style.ERROR('❌ Quantidade deve ser maior que 0')
            )
            return
        
        if quantity > 10000:
            self.stdout.write(
                self.style.ERROR('❌ Quantidade máxima: 10000 produtos')
            )
            return
        
        if min_price >= max_price:
            self.stdout.write(
                self.style.ERROR('❌ Preço mínimo deve ser menor que o máximo')
            )
            return
        
        if not 0 <= low_stock_percent <= 100:
            self.stdout.write(
                self.style.ERROR('❌ Percentual de estoque baixo deve estar entre 0 e 100')
            )
            return
        
        # Verificar se existem categorias
        categories_count = Category.objects.count()
        if categories_count == 0:
            self.stdout.write(
                self.style.ERROR(
                    '\n❌ Nenhuma categoria encontrada!\n'
                    'Crie categorias antes de gerar produtos:\n'
                    '  $ python manage.py create_categories\n'
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
            self.stdout.write('🗑️  Removendo produtos existentes...')
            products_count = Product.objects.count()
            
            if products_count > 0:
                Product.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(f'   ✅ Removidos {products_count} produtos\n')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('   Nenhum produto para remover.\n')
                )
        
        # Buscar categorias disponíveis
        categories = list(Category.objects.all())
        
        self.stdout.write(
            f'📦 Gerando {quantity} produtos com {categories_count} categorias disponíveis...\n'
        )
        
        # Calcular quantos produtos terão estoque baixo
        low_stock_quantity = int(quantity * low_stock_percent / 100)
        
        # Preparar dados
        products_list = []
        used_skus = set(Product.objects.values_list('sku', flat=True))
        created_count = 0
        skipped_count = 0
        
        for i in range(quantity):
            # Definir se terá estoque baixo
            is_low_stock = i < low_stock_quantity
            
            # Gerar dados
            sku = self.generate_sku(fake, used_skus)
            name = self.generate_product_name(fake)
            description = self.generate_description(fake, name)
            price = self.generate_price(fake, min_price, max_price)
            category = fake.random_element(categories)
            minimum_stock = self.generate_minimum_stock(fake)
            stock_quantity = self.generate_stock_quantity(fake, is_low_stock)
            
            # Garantir que estoque baixo seja menor que mínimo
            if is_low_stock and stock_quantity > minimum_stock:
                stock_quantity = fake.random_int(min=0, max=minimum_stock)
            
            # Criar objeto Product
            product = Product(
                sku=sku,
                name=name,
                description=description,
                price=price,
                category=category,
                stock_quantity=stock_quantity,
                minimum_stock=minimum_stock
            )
            products_list.append(product)
            created_count += 1
            
            # Feedback visual a cada 50 produtos
            if (i + 1) % 50 == 0:
                self.stdout.write(f'   ⏳ Processando... {i + 1}/{quantity}')
        
        # Salvar no banco usando bulk_create
        if products_list:
            try:
                with transaction.atomic():
                    Product.objects.bulk_create(
                        products_list,
                        batch_size=100
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\n✅ {created_count} produtos criados com sucesso!\n'
                        )
                    )
                    
                    # Mostrar amostra dos primeiros 5 produtos
                    self.stdout.write('📋 Amostra dos produtos criados:')
                    for i, product in enumerate(products_list[:5], 1):
                        status_emoji = '🔴' if product.stock_quantity <= product.minimum_stock else '🟢'
                        self.stdout.write(
                            f'   {i}. [{product.sku}] {product.name}\n'
                            f'      💰 R$ {product.price} | '
                            f'{status_emoji} Estoque: {product.stock_quantity} '
                            f'(mín: {product.minimum_stock}) | '
                            f'📂 {product.category.name}'
                        )
                    
                    if len(products_list) > 5:
                        self.stdout.write(f'\n   ... e mais {len(products_list) - 5} produtos')
            
            except IntegrityError as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'\n❌ Erro de integridade ao criar produtos: {str(e)}\n'
                        'Possível duplicação de SKU. Tente novamente.'
                    )
                )
                return
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ Erro ao criar produtos: {str(e)}')
                )
                return
        
        # Estatísticas finais
        total_products = Product.objects.count()
        low_stock_count = Product.objects.filter(
            stock_quantity__lte=F('minimum_stock')
        ).count()
        out_of_stock = Product.objects.filter(stock_quantity=0).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 ESTATÍSTICAS:\n'
                f'   Total de produtos: {total_products}\n'
                f'   🔴 Estoque baixo: {low_stock_count}\n'
                f'   ⚫ Sem estoque: {out_of_stock}\n'
                f'   🟢 Estoque normal: {total_products - low_stock_count}\n'
            )
        )
