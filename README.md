# SISTOCK
Sistema de Controle de Estoque baseado em `Django`.

## Sobre o Projeto

O SISTOCK é um sistema completo de controle de estoque desenvolvido em Django, projetado para gerenciar produtos, fornecedores, movimentações de estoque e relatórios de forma eficiente e intuitiva.

### Funcionalidades Principais

- **Gestão de Produtos**: CRUD completo com categorias, SKUs únicos e controle de estoque mínimo
- **Gestão de Fornecedores**: Cadastro e controle de fornecedores com informações de contato
- **Movimentações de Estoque**: Entrada, saída e ajuste de produtos com histórico completo
- **Relatórios**: Exportação de dados em CSV e PDF
- **Dashboard**: Visão geral com alertas de estoque baixo e métricas
- **Sistema de Permissões**: Diferentes níveis de acesso (Admin, Manager, Staff)

<br>

## Pré-requisitos

- Python
- Git

<br>

## Configuração do Ambiente Local

### 1. Clone o repositório
```bash
git clone https://github.com/mateus-s-a/SISTOCK.git
cd SISTOCK
```

### 2. Crie e ative um ambiente virtual
**Windows:**
```text
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

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:
```text
DEBUG=True
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=sqlite:///db.sqlite3
```

### 5. Execute as migrações do banco de dados
```bash
python manage.py migrate
```

### 6. Crie um superusuário (admin)
```bash
python manage.py createsuperuser
```

### 7. Execute o servidor de desenvolvimento
```bash
python manage.py runserver
```
O sistema estará disponível em `http://127.0.0.1:8000/`.

<br>

## Verificação da Instalação
Execute os seguintes comandos para garantir que tudo está funcionando corretamente:

**Verificar configuração do Django:**
```bash
python manage.py check
```

**Executar testes: (quando disponíveis)**
```bash
python manage.py test
```

**Coletar arquivos estáticos: (em produção)**
```bash
python manage.py collectstatic
```

<br>

## Estrutura do Projeto
```text
SISTOCK/
├── apps/
│ ├── accounts/         # Gestão de usuários e perfis
│ ├── inventory/        # Movimentações de estoque
│ ├── products/         # Produtos e categorias
│ ├── reports/          # Relatórios e exportações
│ └── suppliers/        # Fornecedores
├── sistock/
│ ├── settings/         # Configurações por ambiente
│ │ ├── base.py         # Configurações base
│ │ ├── development.py  # Ambiente de desenvolvimento
│ │ └── production.py   # Ambiente de produção
│ └── urls.py           # URLs principais
├── static/             # Arquivos estáticos
├── templates/          # Templates HTML
├── manage.py           # Gerenciador do Django
└── requirements.txt    # Dependências do projeto
```

<br>

## Tecnologias Utilizadas
- **Django**: Framework web em Python
- **Bootstrap**: Framework CSS para design responsivo
- **django-crispy-forms**: Melhora a renderização de formulários
- **django-filter**: Filtragem avançada de consultas
- **ReportLab**: Geração de PDFs
- **OpenPyXL**: Manipulação de arquivos Excel
- **python-decouple**: Gerenciamento de variáveis de ambiente

<br>

## Geração de Dados de Teste com Faker

O projeto utiliza a biblioteca [Faker](https://faker.readthedocs.io/) para gerar dados falsos realistas durante o desenvolvimento e testes.

### Instalação

O Faker já está incluído no `requirements.txt`. Ao instalar as dependências do projeto, ele será instalado automaticamente:

```bash
pip install -r requirements.txt
```

### Uso Básico

O Faker está configurado para gerar dados em **português brasileiro** (`pt_BR`):

```py
from faker import Faker

fake = Faker('pt_BR')
```

### Exemplos

```py
print(fake.name()) # Nome brasileiro
print(fake.company()) # Nome de empresa
print(fake.cnpj()) # CNPJ válido
print(fake.city()) # Cidade brasileira
```

### Comandos de População do Banco

Após a configuração completa, você poderá usar comandos para popular o banco de dados:

### Popular todas as tabelas

```bash
python manage.py create_all_data
```

### Popular apenas categorias

```bash
python manage.py create_categories
```

### Popular apenas produtos

```bash
python manage.py create_products --quantity=50
```

> **Nota:** Os comandos serão implementados nas próximas fases do desenvolvimento.

### Recursos

- [Documentação oficial do Faker](https://faker.readthedocs.io/)
- [Providers do locale pt_BR](https://faker.readthedocs.io/en/master/locales/pt_BR.html)


> (continuação...)