# SISTOCK - Sistema de Controle de Estoque

> Sistema web para gerenciamento de estoque desenvolvido com Django, focado em controle de produtos, movimentações, fornecedores e relatórios gerenciais.

<br>

## Tecnologias

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![JavaScript](https://shields.io/badge/JavaScript-F7DF1E?logo=JavaScript&logoColor=000&style=flat-square)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

**Backend:**
- Django 5.2.7
- Django REST Framework 3.16.1
- PostgreSQL / SQLite
- Redis (caching e rate limiting)
- Pillow 12.0.0 (processamento de imagens)

**Frontend:**
- Bootstrap 5 (via django-crispy-forms)
- Django Select2 (autocomplete avançado)
- Django Filters (filtragem de dados)

**Bibliotecas Auxiliares:**
- Faker 37.12.0 (geração de dados de teste)
- ReportLab 4.4.4 (geração de PDFs)
- OpenPyXL 3.1.5 (exportação Excel)
- Python-Decouple 3.8 (gerenciamento de variáveis de ambiente)
- WhiteNoise 6.11.0 (servir arquivos estáticos em produção)

<br>

##  Pré-requisitos

- `Python 3.11` ou superior
- `pip` (gerenciador de pacotes Python)
- `Git`
- `PostgreSQL` (para produção) ou `SQLite` (para desenvolvimento)
- `Redis` (opcional, para cache e rate limiting)

<br>

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/mateus-s-a/SISTOCK.git
cd SISTOCK
```

### 2. Crie e ative um ambiente virtual

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/MacOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configuração do Banco de Dados

#### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações de Segurança
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True

# Banco de Dados (Desenvolvimento - SQLite)
# Não é necessário configurar para SQLite em desenvolvimento

# Banco de Dados (Produção - PostgreSQL)
DATABASE_URL=postgresql://usuario:senha@localhost:5432/sistock_db

# Redis (Opcional)
REDIS_URL=redis://localhost:6379/0

# Configurações de Email (Opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
EMAIL_USE_TLS=True
```

#### Criação do banco de dados

**Desenvolvimento (SQLite):**
O banco SQLite é criado automaticamente ao executar as migrações.

**Produção (PostgreSQL):**
```bash
# Acesse o PostgreSQL
psql -U postgres

# Crie o banco de dados
CREATE DATABASE sistock_db;
CREATE USER sistock_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE sistock_db TO sistock_user;
\q
```

#### Executar migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Popular dados iniciais

O **SISTOCK** oferece comandos personalizados para [população rápida do banco de dados](https://github.com/mateus-s-a/SISTOCK/blob/main/docs/faker-guide.md) usando a biblioteca `Faker`.

**Criar todos os modelos (popular rapidamente por completo):
```bash
python manage.py create_all_data
```

**Criar categorias de produtos:**
```bash
python manage.py create_categories
```

**Criar produtos (requer categorias criadas):**
```bash
python manage.py create_products
```

**Criar usuário administrador:**
```bash
python manage.py createsuperuser
```

**Carregar fixtures (dados pré-configurados):**
```bash
python manage.py loaddata apps/products/fixtures/categories.json
```

### 5. Execute o servidor de desenvolvimento

**Ambiente de Desenvolvimento:**
```bash
# Define o ambiente como desenvolvimento
set DJANGO_SETTINGS_MODULE=sistock.settings.development  # Windows
export DJANGO_SETTINGS_MODULE=sistock.settings.development  # Linux/Mac

python manage.py runserver
```

**Ambiente de Produção:**
```bash
set DJANGO_SETTINGS_MODULE=sistock.settings.production  # Windows
export DJANGO_SETTINGS_MODULE=sistock.settings.production  # Linux/Mac

python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
```

Acesse: [http://127.0.0.1:8000](http://127.0.0.1:8000)

<br>

## Funcionalidades Implementadas

### Gestão de Produtos
- [x] CRUD completo de produtos com imagem
- [x] Categorização hierárquica de produtos
- [x] Controle de estoque mínimo com alertas
- [x] Busca e filtragem avançada (nome, categoria, fornecedor)
- [x] Código de barras / SKU único
- [x] Status de ativação/desativação

### Gestão de Fornecedores
- [x] CRUD de fornecedores
- [x] Dados de contato (telefone, email, endereço)
- [x] Vinculação com produtos fornecidos
- [x] Filtros por nome e status

### Controle de Movimentações
- [x] Registro de entradas e saídas de estoque
- [x] Histórico completo de movimentações
- [x] Associação com fornecedores (entradas)
- [x] Motivos de movimentação personalizados
- [x] Auditoria automática (usuário, data, hora)

### Dashboard e Relatórios
- [x] Dashboard com indicadores em tempo real
- [x] Total de produtos, valor do estoque, alertas
- [x] Produtos com estoque crítico
- [x] Últimas movimentações
- [x] Geração de relatórios em PDF (ReportLab)
- [x] Exportação de dados em Excel (OpenPyXL)

### Autenticação e Segurança
- [x] Sistema de login/logout
- [x] Controle de permissões por app (accounts, inventory, products, suppliers, reports)
- [x] Rate limiting com django-ratelimit
- [x] Cache com Redis
- [x] Proteção CSRF e XSS

### Interface e Usabilidade
- [x] Interface responsiva com Bootstrap 5
- [x] Formulários com django-crispy-forms
- [x] Select2 para autocomplete em formulários
- [x] Paginação otimizada
- [x] Mensagens de feedback (success, error, warning)
- [x] Localização em português brasileiro

<br>

## Arquitetura

O SISTOCK segue a arquitetura MVT (Model-View-Template) do Django com estrutura modular:

```
SISTOCK/
├── apps/
│   ├── accounts/          # Gestão de usuários e autenticação
│   ├── inventory/         # Movimentações de estoque
│   ├── products/          # Gestão de produtos e categorias
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── create_categories.py  # Comando para popular categorias
│   │   │       └── create_products.py    # Comando para popular produtos
│   │   ├── fixtures/      # Dados iniciais (JSON)
│   │   ├── models.py      # Modelos: Product, Category
│   │   ├── views.py       # Views CBV (ListView, CreateView, etc)
│   │   └── urls.py        # Rotas do app
│   ├── suppliers/         # Gestão de fornecedores
│   └── reports/           # Relatórios e exportações
├── sistock/
│   ├── settings/
│   │   ├── base.py        # Configurações base
│   │   ├── development.py # Configurações de desenvolvimento
│   │   └── production.py  # Configurações de produção
│   └── urls.py            # Rotas principais
├── templates/             # Templates HTML globais
├── static/                # Arquivos estáticos (CSS, JS, imagens)
├── media/                 # Upload de arquivos (imagens de produtos)
├── requirements.txt       # Dependências do projeto
└── manage.py              # Script de gerenciamento Django
```

### Padrões Utilizados
- **Models:** ORM Django com relacionamentos ForeignKey e ManyToMany
- **Views:** Class-Based Views (ListView, DetailView, CreateView, UpdateView, DeleteView)
- **Forms:** ModelForms com validações personalizadas
- **Templates:** Herança de templates com `base.html`
- **Mixins:** LoginRequiredMixin, PermissionRequiredMixin para controle de acesso

<br>

## Endpoints da API

### Rotas Principais

```python
# Autenticação (apps/accounts/)
/accounts/login/          # Login
/accounts/logout/         # Logout
/accounts/register/       # Registro de usuário

# Dashboard (apps/inventory/)
/inventory/dashboard/     # Dashboard principal
/inventory/movements/     # Lista de movimentações
/inventory/movements/add/ # Adicionar movimentação

# Produtos (apps/products/)
/products/                # Lista de produtos
/products/add/            # Adicionar produto
/products/<id>/           # Detalhe do produto
/products/<id>/edit/      # Editar produto
/products/<id>/delete/    # Deletar produto
/products/categories/     # Lista de categorias
/products/api/products/   # API REST (JSON)

# Fornecedores (apps/suppliers/)
/suppliers/               # Lista de fornecedores
/suppliers/add/           # Adicionar fornecedor
/suppliers/<id>/edit/     # Editar fornecedor
/suppliers/<id>/delete/   # Deletar fornecedor

# Relatórios (apps/reports/)
/reports/stock/           # Relatório de estoque
/reports/movements/       # Relatório de movimentações
/reports/export/pdf/      # Exportar PDF
/reports/export/excel/    # Exportar Excel

# Admin
/admin/                   # Painel administrativo Django
```

<br>

## Modelo de Dados

### Principais Modelos

**Product** (`apps/products/models.py`):
```python
- name: CharField (nome do produto)
- description: TextField (descrição)
- sku: CharField (código único)
- category: ForeignKey (categoria)
- supplier: ForeignKey (fornecedor)
- price: DecimalField (preço)
- stock_quantity: PositiveIntegerField (quantidade em estoque)
- min_stock: PositiveIntegerField (estoque mínimo)
- image: ImageField (imagem do produto)
- is_active: BooleanField (status)
- created_at, updated_at: DateTimeField
```

**Category** (`apps/products/models.py`):
```python
- name: CharField
- description: TextField
- parent: ForeignKey (categoria pai - hierarquia)
```

**StockMovement** (`apps/inventory/models.py`):
```python
- product: ForeignKey
- type: CharField (ENTRADA/SAIDA)
- quantity: PositiveIntegerField
- reason: CharField
- user: ForeignKey (usuário responsável)
- supplier: ForeignKey (opcional)
- date: DateTimeField
```

**Supplier** (`apps/suppliers/models.py`):
```python
- name: CharField
- contact_person: CharField
- email: EmailField
- phone: CharField
- address: TextField
- is_active: BooleanField
```

### Relacionamentos
- Product → Category (N:1)
- Product → Supplier (N:1)
- StockMovement → Product (N:1)
- StockMovement → User (N:1)
- StockMovement → Supplier (N:1, opcional)

<br>

## Testes

```bash
# Executar todos os testes
python manage.py test

# Testar app específico
python manage.py test apps.products

# Testes com cobertura
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

<br>

## Segurança

- [x] Proteção CSRF habilitada
- [x] Rate limiting em endpoints críticos
- [x] Validação de permissões em todas as views
- [x] Senhas hasheadas com PBKDF2
- [x] Variáveis sensíveis em arquivos .env (não versionados)
- [x] WhiteNoise para servir arquivos estáticos com segurança

<br>

## Documentação Adicional

- [Django Documentation](https://docs.djangoproject.com/en/5.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)
- [Faker Documentation](https://faker.readthedocs.io/)

<br>

## Licença

Este projeto está sob licença livre para fins educacionais.

<br>

## Autor

**Mateus de S. Arruda**
- GitHub: [@mateus-s-a](https://github.com/mateus-s-a)
- Repositório: [SISTOCK](https://github.com/mateus-s-a/SISTOCK)
