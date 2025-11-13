"""
Management command para popular a tabela Supplier com dados de teste.
Uso: python manage.py create_suppliers [opções]
"""

from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from faker import Faker
from apps.suppliers.models import Supplier


class Command(BaseCommand):
    """
    Comando para criar fornecedores usando Faker.
    """
    
    help = 'Popula a tabela Supplier com fornecedores de teste gerados dinamicamente'
    
    # Sufixos comuns em empresas brasileiras
    COMPANY_SUFFIXES = [
        'Ltda', 'S.A.', 'EIRELI', 'ME', 'EPP', 'Comércio',
        'Indústria e Comércio', 'Distribuidora', 'Importadora',
        'Materiais', 'Suprimentos', 'Tecnologia', 'Soluções'
    ]
    
    # Tipos de empresas fornecedoras
    BUSINESS_TYPES = [
        'Distribuidora', 'Atacadista', 'Importadora', 'Fabricante',
        'Representações', 'Comércio', 'Indústria', 'Comercial',
        'Suprimentos', 'Materiais', 'Produtos', 'Equipamentos'
    ]
    
    def add_arguments(self, parser):
        """
        Define argumentos aceitos pelo comando.
        """
        parser.add_argument(
            '--quantity',
            type=int,
            default=30,
            help='Quantidade de fornecedores a criar (padrão: 30)'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todos os fornecedores existentes antes de criar novos'
        )
        
        parser.add_argument(
            '--seed',
            type=int,
            default=None,
            help='Seed para gerar dados reproduzíveis (opcional)'
        )
    
    def generate_cnpj(self, fake):
        """
        Gera um CNPJ no formato brasileiro: XX.XXX.XXX/XXXX-XX
        
        Args:
            fake: Instância do Faker
            
        Returns:
            str: CNPJ formatado
        """
        # Gerar números aleatórios
        part1 = fake.numerify(text='##')
        part2 = fake.numerify(text='###')
        part3 = fake.numerify(text='###')
        part4 = fake.numerify(text='####')
        part5 = fake.numerify(text='##')
        
        return f"{part1}.{part2}.{part3}/{part4}-{part5}"
    
    def generate_company_name(self, fake):
        """
        Gera um nome de empresa brasileiro realista.
        
        Args:
            fake: Instância do Faker
            
        Returns:
            str: Nome da empresa
        """
        patterns = [
            # Padrão 1: Sobrenome + Sufixo
            lambda: f"{fake.last_name()} {fake.random_element(self.COMPANY_SUFFIXES)}",
            
            # Padrão 2: Nome Completo + Sufixo
            lambda: f"{fake.last_name()} & {fake.last_name()} {fake.random_element(self.COMPANY_SUFFIXES)}",
            
            # Padrão 3: Tipo de negócio + Nome + Sufixo
            lambda: f"{fake.random_element(self.BUSINESS_TYPES)} {fake.last_name()} {fake.random_element(self.COMPANY_SUFFIXES)}",
            
            # Padrão 4: Nome + Tipo de negócio
            lambda: f"{fake.last_name()} {fake.random_element(self.BUSINESS_TYPES)}",
            
            # Padrão 5: Iniciais + Tipo
            lambda: f"{fake.lexify(text='??', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')} {fake.random_element(self.BUSINESS_TYPES)} {fake.random_element(self.COMPANY_SUFFIXES)}"
        ]
        
        pattern = fake.random_element(patterns)
        return pattern()
    
    def generate_phone(self, fake):
        """
        Gera telefone no formato brasileiro.
        
        Returns:
            str: Telefone formatado
        """
        # 70% celular, 30% fixo
        if fake.random_int(min=1, max=100) <= 70:
            # Celular: (XX) 9XXXX-XXXX
            ddd = fake.numerify(text='##')
            first = fake.numerify(text='9####')
            second = fake.numerify(text='####')
            return f"({ddd}) {first}-{second}"
        else:
            # Fixo: (XX) XXXX-XXXX
            ddd = fake.numerify(text='##')
            first = fake.numerify(text='####')
            second = fake.numerify(text='####')
            return f"({ddd}) {first}-{second}"
    
    def generate_email(self, fake, company_name):
        """
        Gera email corporativo baseado no nome da empresa.
        
        Args:
            fake: Instância do Faker
            company_name: Nome da empresa
            
        Returns:
            str: Email corporativo
        """
        # Pegar primeira palavra do nome da empresa
        first_word = company_name.split()[0].lower()
        
        # Remover acentos e caracteres especiais
        first_word = first_word.replace('ç', 'c')
        first_word = ''.join(c for c in first_word if c.isalnum())
        
        # Prefixos comuns de email corporativo
        prefixes = ['contato', 'vendas', 'comercial', 'suprimentos', 'atendimento']
        prefix = fake.random_element(prefixes)
        
        # Domínios comuns
        domains = ['com.br', 'net.br', 'ind.br', 'com']
        domain = fake.random_element(domains)
        
        return f"{prefix}@{first_word}.{domain}"
    
    def generate_address(self, fake):
        """
        Gera endereço brasileiro completo.
        
        Args:
            fake: Instância do Faker
            
        Returns:
            str: Endereço formatado
        """
        street = fake.street_address()
        neighborhood = fake.bairro()
        city = fake.city()
        state = fake.state_abbr()
        postcode = fake.postcode()
        
        return f"{street}, {neighborhood}, {city} - {state}, CEP: {postcode}"
    
    def handle(self, *args, **options):
        """
        Lógica principal do comando.
        """
        quantity = options['quantity']
        clear = options['clear']
        seed = options['seed']
        
        # Validações
        if quantity < 1:
            self.stdout.write(
                self.style.ERROR('❌ Quantidade deve ser maior que 0')
            )
            return
        
        if quantity > 1000:
            self.stdout.write(
                self.style.ERROR('❌ Quantidade máxima: 1000 fornecedores')
            )
            return
        
        # Inicializar Faker
        fake = Faker('pt_BR')
        if seed is not None:
            Faker.seed(seed)
            self.stdout.write(f'🌱 Usando seed: {seed}')
        
        # Limpar dados se solicitado
        if clear:
            self.stdout.write('🗑️  Removendo fornecedores existentes...')
            suppliers_count = Supplier.objects.count()
            
            if suppliers_count > 0:
                Supplier.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(
                        f'   ✅ Removidos {suppliers_count} fornecedores\n'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING('   Nenhum fornecedor para remover.\n')
                )
        
        # Gerar fornecedores
        self.stdout.write(f'📦 Gerando {quantity} fornecedores...\n')
        
        suppliers_list = []
        created_count = 0
        
        for i in range(quantity):
            # Gerar dados
            company_name = self.generate_company_name(fake)
            contact_person = fake.name()
            email = self.generate_email(fake, company_name)
            phone = self.generate_phone(fake)
            address = self.generate_address(fake)
            cnpj = self.generate_cnpj(fake)
            
            # Criar objeto Supplier
            supplier = Supplier(
                name=company_name,
                contact_person=contact_person,
                email=email,
                phone=phone,
                address=address,
                cnpj=cnpj
            )
            suppliers_list.append(supplier)
            created_count += 1
            
            # Feedback visual a cada 20 fornecedores
            if (i + 1) % 20 == 0:
                self.stdout.write(f'   ⏳ Processando... {i + 1}/{quantity}')
        
        # Salvar no banco usando bulk_create
        if suppliers_list:
            try:
                with transaction.atomic():
                    Supplier.objects.bulk_create(
                        suppliers_list,
                        batch_size=100
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\n✅ {created_count} fornecedores criados com sucesso!\n'
                        )
                    )
                    
                    # Mostrar amostra dos primeiros 5 fornecedores
                    self.stdout.write('📋 Amostra dos fornecedores criados:')
                    for i, supplier in enumerate(suppliers_list[:5], 1):
                        self.stdout.write(
                            f'\n   {i}. {supplier.name}\n'
                            f'      CNPJ: {supplier.cnpj}\n'
                            f'      Contato: {supplier.contact_person}\n'
                            f'      📧 {supplier.email}\n'
                            f'      📞 {supplier.phone}\n'
                            f'      📍 {supplier.address[:50]}...'
                        )
                    
                    if len(suppliers_list) > 5:
                        self.stdout.write(
                            f'\n   ... e mais {len(suppliers_list) - 5} fornecedores'
                        )
            
            except IntegrityError as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'\n❌ Erro de integridade ao criar fornecedores: {str(e)}'
                    )
                )
                return
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'\n❌ Erro ao criar fornecedores: {str(e)}'
                    )
                )
                return
        
        # Estatísticas finais
        total_suppliers = Supplier.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 Total de fornecedores no banco: {total_suppliers}\n'
            )
        )
