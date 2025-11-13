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
$ python manage.py create_products
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
$ python manage.py create_categories --quantity=15
```
#### Criar 50 produtos (padrão)

```bash
$ python manage.py create_products
```
#### Criar 100 produtos

```bash
$ python manage.py create_products --quantity=100 --clear
```
#### Produtos baratos (R$ 10 a R$ 200)

```bash
$ python manage.py create_products --quantity=50 --min-price=10 --max-price=200 --clear
```
#### 50% dos produtos com estoque baixo

```bash
$ python manage.py create_products --quantity=30 --low-stock-percent=50 --clear
```
#### Dados reproduzíveis para testes

```bash
$ python manage.py create_products --quantity=20 --seed=42 --clear
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
$ python manage.py create_categories
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
$ python manage.py create_categories
```

#### Criar 50 categorias aleatórias

```bash
$ python manage.py create_categories --quantity=50
```

#### Limpar e criar 100 categorias

```bash
$ python manage.py create_categories --quantity=100 --clear
```

### Limpar TUDO (produtos + categorias) e recriar

```bash
$ python manage.py create_categories --quantity=20 --clear --force
```

#### Criar 20 categorias simples (sem modificadores)

```bash
$ python manage.py create_categories --quantity=20 --simple
```

#### Criar com seed para testes reproduzíveis

```bash
$ python manage.py create_categories --quantity=10 --seed=42 --clear
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


<br>

---

<br>


### Fornecedores (`create_suppliers`)

Popula a tabela `Supplier` com fornecedores brasileiros gerados dinamicamente.

**Uso básico:**

```bash
$ python manage.py create_suppliers
```

**Opções:**

- `--quantity N`: Cria N fornecedores (padrão: 30, máximo: 1000)
- `--clear`: Remove todos os fornecedores antes de criar novos
- `--seed N`: Define seed para reprodutibilidade

**Exemplos:**

#### Criar 30 fornecedores (padrão)

```bash
$ python manage.py create_suppliers
```

#### Criar 50 fornecedores

```bash
$ python manage.py create_suppliers --quantity=50 --clear
```

#### Dados reproduzíveis para testes

```bash
$ python manage.py create_suppliers --quantity=20 --seed=42 --clear
```

**Recursos:**

- **Nomes realistas:** Empresas brasileiras típicas (Silva & Oliveira Ltda, etc)
- **CNPJs formatados:** Padrão XX.XXX.XXX/XXXX-XX
- **Emails corporativos:** Baseados no nome da empresa
- **Telefones brasileiros:** Celulares (9XXXX-XXXX) e fixos
- **Endereços completos:** Com bairro, cidade, estado e CEP

#### Nome da empresa



<br>

---

<br>



### Movimentações de Estoque (`create_movements`)

Popula a tabela `StockMovement` com movimentações de estoque e atualiza quantidades dos produtos.

**Pré-requisitos:** Produtos criados e pelo menos um usuário no sistema.

**Uso básico:**

```bash
$ python manage.py create_movements
```

**Opções:**

- `--quantity N`: Cria N movimentações (padrão: 200, máximo: 10000)
- `--clear`: Remove movimentações e reseta estoques
- `--seed N`: Define seed para reprodutibilidade
- `--days N`: Distribui movimentações nos últimos N dias (padrão: 90)
- `--update-stock`: Atualiza estoque dos produtos (padrão: True)

**Exemplos:**

#### Criar 200 movimentações (padrão)

```bash
$ python manage.py create_movements
```
#### 500 movimentações nos últimos 30 dias

```bash
$ python manage.py create_movements --quantity=500 --days=30 --clear
```
#### Dados reproduzíveis

```bash
$ python manage.py create_movements --quantity=300 --seed=42 --clear
```

**Recursos:**

- **Distribuição realista:** 40% entradas, 45% saídas, 15% ajustes
- **Datas distribuídas:** Últimos 90 dias por padrão
- **Razões contextuais:** Motivos específicos para cada tipo
- **Atualização automática:** Estoques atualizados conforme movimentações
- **Quantidades lógicas:** Entradas maiores, saídas menores



<br>

---

<br>
