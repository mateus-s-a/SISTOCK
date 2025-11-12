# Guia de Uso do Faker no SISTOCK

Este documento fornece exemplos práticos de como usar a biblioteca Faker no projeto SISTOCK.

## Configuração Inicial

```py
from faker import Faker
```

## Inicializar com localização brasileira

```py
fake = Faker('pt_BR')
```

## Para resultados reproduzíveis (útil em testes)

```py
Faker.seed(12345)
```

<br>

---

<br>

## Exemplos de Geração de Dados



### Produtos (`create_products`)

Popula a tabela `Product` com produtos gerados dinamicamente usando Faker.

**Pré-requisito:** É necessário ter categorias criadas antes de executar este comando.

**Uso básico:**
```bash
python manage.py create_products
```


**Opções:**

- `--quantity N`: Cria N produtos (padrão: 50, máximo: 10000)
- `--clear`: Remove todos os produtos antes de criar novos
- `--seed N`: Define seed para reprodutibilidade
- `--min-price X`: Preço mínimo (padrão: 10.00)
- `--max-price Y`: Preço máximo (padrão: 5000.00)
- `--low-stock-percent P`: Percentual com estoque baixo (padrão: 20%)

**Exemplos:**

#### Criar categorias primeiro

```bash
python manage.py create_categories --quantity=15
```
#### Criar 50 produtos (padrão)

```bash
python manage.py create_products
```
#### Criar 100 produtos

```bash
python manage.py create_products --quantity=100 --clear
```
#### Produtos baratos (R$ 10 a R$ 200)

```bash
python manage.py create_products --quantity=50 --min-price=10 --max-price=200 --clear
```
#### 50% dos produtos com estoque baixo

```bash
python manage.py create_products --quantity=30 --low-stock-percent=50 --clear
```
#### Dados reproduzíveis para testes

```bash
python manage.py create_products --quantity=20 --seed=42 --clear
```

**Recursos:**

- **SKUs únicos:** Formato `ABC123456` (3 letras + 6 números)
- **Nomes realistas:** Combinação de adjetivos, tipos e descritores
- **Preços convincentes:** Terminam em .90, .95 ou .99 (70% dos casos)
- **Estoque variado:** Normal (20-500) ou baixo (0-10)
- **Vinculação automática:** Distribui produtos entre categorias existentes


<br>

---

<br>


### Categorias (`create_categories`)

#### Categorias de produtos

Popula a tabela `Category` com categorias geradas dinamicamente usando Faker.


**Uso básico:**

```bash
python manage.py create_categories
```

**Opções:**

- `--quantity N`: Cria N categorias (padrão: 15, máximo: 1000)
- `--clear`: Remove todas as categorias antes de criar novas
- `--seed N`: Define seed para reprodutibilidade
- `--simple`: Gera apenas nomes simples sem modificadores
- `--force`: Força remoção de produtos ao usar --clear (USE COM CUIDADO!)

**Exemplos:**

#### Criar 15 categorias (padrão)

```bash
python manage.py create_categories
```

#### Criar 50 categorias aleatórias

```bash
python manage.py create_categories --quantity=50
```

#### Limpar e criar 100 categorias

```bash
python manage.py create_categories --quantity=100 --clear
```

### Limpar TUDO (produtos + categorias) e recriar

```bash
python manage.py create_categories --quantity=20 --clear --force
```

#### Criar 20 categorias simples (sem modificadores)

```bash
python manage.py create_categories --quantity=20 --simple
```

#### Criar com seed para testes reproduzíveis

```bash
python manage.py create_categories --quantity=10 --seed=42 --clear
```

**Como funciona:**

O comando combina elementos de duas listas:

1. **Bases de categorias** (50+ opções): Eletrônicos, Móveis, Alimentos, etc.
2. **Modificadores** (20+ opções): Premium, Profissional, Infantil, etc.

Exemplos de categorias geradas:
- Eletrônicos Premium
- Móveis Profissional  
- Beleza Sustentável
- Esportes Infantil
- Livros Digital
- Alimentos Orgânico

Cada categoria recebe uma descrição automática e realista.


#### Descrição de categoria

```py
description = fake.text(max_nb_chars=200)
```

### Fornecedores

```py
from faker import Faker

fake = Faker('pt_BR')
```

#### Nome da empresa

```py
company_name = fake.company()
CNPJ (formato: XX.XXX.XXX/XXXX-XX)

cnpj = fake.numerify(text='##.###.###/####-##')
```

#### Nome do contato

```py
contact_name = fake.name()
```

#### Email corporativo

```py
email = fake.company_email()
```

#### Telefone (formato brasileiro)

```py
phone = fake.phone_number()
```

#### Endereço completo

```py
address = fake.street_address()
city = fake.city()
state = fake.state()
postal_code = fake.postcode()

print(f"Empresa: {company_name}")
print(f"CNPJ: {cnpj}")
print(f"Contato: {contact_name}")
print(f"Email: {email}")
print(f"Telefone: {phone}")
print(f"Endereço: {address}, {city} - {state}, CEP: {postal_code}")
```

### Movimentações de Estoque

```py
from faker import Faker
from datetime import datetime

fake = Faker('pt_BR')
```

#### Tipo de movimentação

```py
movement_types = ['entrada', 'saida', 'ajuste']
movement_type = fake.random_element(elements=movement_types)
```

#### Quantidade

```py
quantity = fake.random_int(min=1, max=100)
```

#### Data (últimos 90 dias)

```py
movement_date = fake.date_between(start_date='-90d', end_date='today')
```

#### Razão/Descrição

```py
reasons = {
    'entrada': [
        'Compra de fornecedor',
        'Devolução de cliente',
        'Transferência de estoque'
    ],
    'saida': [
        'Venda ao cliente',
        'Devolução ao fornecedor',
        'Perda/Avaria'
    ],
    'ajuste': [
        'Correção de inventário',
        'Ajuste por auditoria',
        'Correção de lançamento'
    ]
}

reason = fake.random_element(elements=reasons[movement_type])

print(f"Tipo: {movement_type}")
print(f"Quantidade: {quantity}")
print(f"Data: {movement_date}")
print(f"Razão: {reason}")
```

## Dicas e Boas Práticas

### 1. Usar Seed para Testes Reproduzíveis

```py
Faker.seed(0) # Sempre gera os mesmos dados
```

### 2. Gerar Múltiplos Registros

```py
fake = Faker('pt_BR')

products = []
for i in range(100):
    products.append({
        'name': fake.word().capitalize(),
        'sku': fake.lexify(text='???######'),
        'price': fake.pydecimal(left_digits=4, right_digits=2, positive=True)
    })
```

### 3. Evitar Duplicatas

#### Para SKUs únicos

```py
used_skus = set()

def generate_unique_sku():
while True:
sku = fake.lexify(text='???') + fake.numerify(text='######')
if sku not in used_skus:
used_skus.add(sku)
return sku
```
