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

## Exemplos de Geração de Dados

### Produtos

```py
from faker import Faker

fake = Faker('pt_BR')
```

### Nome de produto

```py
product_name = fake.word().capitalize() + " " + fake.word().capitalize()
```

### SKU único (3 letras + 6 números)

```py
sku = fake.lexify(text='???', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ') + fake.numerify(text='######')
```

### Preço

```py
price = fake.pydecimal(left_digits=4, right_digits=2, positive=True, min_value=10, max_value=5000)
```

### Quantidade em estoque

```py
stock_quantity = fake.random_int(min=0, max=500)
```

### Estoque mínimo

```py
minimum_stock = fake.random_int(min=5, max=50)

print(f"Produto: {product_name}")
print(f"SKU: {sku}")
print(f"Preço: R$ {price}")
print(f"Estoque: {stock_quantity}")
print(f"Estoque Mínimo: {minimum_stock}")
```

### Categorias

#### Categorias de produtos

```py
categories = [
    "Eletrônicos",
    "Móveis",
    "Alimentos",
    "Vestuário",
    "Livros",
    "Brinquedos",
    "Ferramentas",
    "Esportes",
    "Beleza",
    "Informática"
]
```

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
