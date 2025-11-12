"""
Management command para popular a tabela Category com dados de teste.
Uso: python manage.py create_categories [opções]
"""

from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from faker import Faker
from apps.products.models import Category


class Command(BaseCommand):
    """
    Comando para criar categorias de produtos usando Faker.
    """
    
    help = 'Popula a tabela Category com categorias de produtos de teste geradas dinamicamente'
    
    # Lista de bases para categorias (português brasileiro)
    CATEGORY_BASES = [
        'Eletrônicos', 'Informática', 'Móveis', 'Alimentos', 'Bebidas',
        'Vestuário', 'Calçados', 'Acessórios', 'Livros', 'Papelaria',
        'Brinquedos', 'Games', 'Ferramentas', 'Esportes', 'Fitness',
        'Beleza', 'Cosméticos', 'Higiene', 'Casa', 'Jardim', 'Decoração',
        'Automotivo', 'Pet Shop', 'Saúde', 'Medicamentos', 'Construção',
        'Material Elétrico', 'Telefonia', 'Áudio', 'Vídeo', 'Fotografia',
        'Instrumentos Musicais', 'Arte', 'Artesanato', 'Cama', 'Mesa',
        'Banho', 'Cozinha', 'Utilidades Domésticas', 'Eletroportáteis',
        'Climatização', 'Iluminação', 'Segurança', 'Escritório',
        'Escola', 'Festa', 'Viagem', 'Camping', 'Pesca', 'Náutica'
    ]
    
    CATEGORY_MODIFIERS = [
        'Profissional', 'Premium', 'Básico', 'Infantil', 'Adulto',
        'Feminino', 'Masculino', 'Unissex', 'Importado', 'Nacional',
        'Sustentável', 'Ecológico', 'Digital', 'Manual', 'Automático',
        'Portátil', 'Industrial', 'Doméstico', 'Comercial', 'Esportivo'
    ]
    
    def add_arguments(self, parser):
        """
        Define argumentos aceitos pelo comando.
        """
        parser.add_argument(
            '--quantity',
            type=int,
            default=15,
            help='Quantidade de categorias a criar (padrão: 15)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todas as categorias existentes antes de criar novas'
        )
        
        parser.add_argument(
            '--seed',
            type=int,
            default=None,
            help='Seed para gerar dados reproduzíveis (opcional)'
        )
        
        parser.add_argument(
            '--simple',
            action='store_true',
            help='Usa apenas nomes simples sem modificadores'
        )
    
    def generate_category_name(self, fake, simple=False, used_names=None):
        """
        Gera um nome de categoria único e realista.
        
        Args:
            fake: Instância do Faker
            simple: Se True, gera nomes simples sem modificadores
            used_names: Set com nomes já utilizados
            
        Returns:
            str: Nome da categoria
        """
        if used_names is None:
            used_names = set()
        
        max_attempts = 50
        
        for _ in range(max_attempts):
            if simple:
                # Nome simples: apenas a categoria base
                name = fake.random_element(elements=self.CATEGORY_BASES)
            else:
                # 70% de chance de adicionar modificador
                if fake.random_int(min=1, max=100) <= 70:
                    modifier = fake.random_element(elements=self.CATEGORY_MODIFIERS)
                    base = fake.random_element(elements=self.CATEGORY_BASES)
                    
                    # 50% de chance do modificador vir antes ou depois
                    if fake.boolean():
                        name = f"{modifier} {base}"
                    else:
                        name = f"{base} {modifier}"
                else:
                    name = fake.random_element(elements=self.CATEGORY_BASES)
            
            # Verificar unicidade
            if name not in used_names:
                used_names.add(name)
                return name
        
        # Fallback: se não conseguir gerar único, adiciona número
        base_name = fake.random_element(elements=self.CATEGORY_BASES)
        counter = 1
        name = f"{base_name} {counter}"
        
        while name in used_names:
            counter += 1
            name = f"{base_name} {counter}"
        
        used_names.add(name)
        return name
    
    def generate_description(self, fake, category_name):
        """
        Gera uma descrição realista para a categoria.
        
        Args:
            fake: Instância do Faker
            category_name: Nome da categoria
            
        Returns:
            str: Descrição da categoria
        """
        templates = [
            f"Produtos de {category_name.lower()} com qualidade garantida e preços competitivos.",
            f"Linha completa de {category_name.lower()} para atender suas necessidades.",
            f"Variedade em {category_name.lower()} das melhores marcas do mercado.",
            f"Seção especializada em {category_name.lower()} com produtos selecionados.",
            f"{category_name} de alta qualidade para uso profissional e doméstico.",
            f"Encontre tudo em {category_name.lower()} em um só lugar.",
            f"Categoria dedicada a {category_name.lower()} com os melhores preços.",
            f"Ampla seleção de {category_name.lower()} para todos os perfis.",
        ]
        
        return fake.random_element(elements=templates)
    
    def handle(self, *args, **options):
        """
        Lógica principal do comando.
        """
        quantity = options['quantity']
        clear = options['clear']
        seed = options['seed']
        simple = options['simple']
        
        # Validar quantidade
        if quantity < 1:
            self.stdout.write(
                self.style.ERROR('❌ Quantidade deve ser maior que 0')
            )
            return
        
        if quantity > 1000:
            self.stdout.write(
                self.style.ERROR('❌ Quantidade máxima: 1000 categorias')
            )
            return
        
        # Inicializar Faker
        fake = Faker('pt_BR')
        if seed is not None:
            Faker.seed(seed)
            self.stdout.write(f'🌱 Usando seed: {seed}')
        
        # Limpar dados se solicitado
        if clear:
            self.stdout.write('🗑️  Removendo categorias existentes...')
            deleted_count = Category.objects.all().count()
            Category.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'   Removidas {deleted_count} categorias')
            )
        
        # Gerar categorias
        self.stdout.write(f'\n📦 Gerando {quantity} categorias...\n')
        
        categories_list = []
        used_names = set()
        created_count = 0
        skipped_count = 0
        
        # Buscar nomes já existentes no banco
        existing_names = set(
            Category.objects.values_list('name', flat=True)
        )
        used_names.update(existing_names)
        
        for i in range(quantity):
            # Gerar nome único
            name = self.generate_category_name(fake, simple, used_names)
            
            # Verificar se já existe no banco (segurança extra)
            if Category.objects.filter(name=name).exists():
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'   ⚠️  [{i+1}/{quantity}] "{name}" já existe. Pulando...'
                    )
                )
                continue
            
            # Gerar descrição
            description = self.generate_description(fake, name)
            
            # Criar objeto Category
            category = Category(
                name=name,
                description=description
            )
            categories_list.append(category)
            created_count += 1
            
            # Feedback visual a cada 10 categorias
            if (i + 1) % 10 == 0:
                self.stdout.write(f'   ⏳ Processando... {i + 1}/{quantity}')
        
        # Salvar no banco usando bulk_create
        if categories_list:
            try:
                with transaction.atomic():
                    Category.objects.bulk_create(
                        categories_list,
                        batch_size=100  # Processar em lotes de 100
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\n✅ {created_count} categorias criadas com sucesso!\n'
                        )
                    )
                    
                    # Mostrar amostra das primeiras 10 categorias criadas
                    self.stdout.write('📋 Amostra das categorias criadas:')
                    for i, cat in enumerate(categories_list[:10], 1):
                        self.stdout.write(f'   {i}. {cat.name}')
                    
                    if len(categories_list) > 10:
                        self.stdout.write(f'   ... e mais {len(categories_list) - 10} categorias')
            
            except IntegrityError as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'\n❌ Erro de integridade ao criar categorias: {str(e)}\n'
                        'Tente usar a flag --clear para limpar dados anteriores.'
                    )
                )
                return
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ Erro ao criar categorias: {str(e)}')
                )
                return
        else:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Nenhuma categoria nova foi criada.'
                )
            )
        
        # Estatísticas finais
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠️  {skipped_count} categorias já existiam')
            )
        
        total_categories = Category.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 Total de categorias no banco: {total_categories}'
            )
        )
