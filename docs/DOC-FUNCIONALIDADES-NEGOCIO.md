## 1. Movimentação de Estoque com Atualização Automática

### Arquitetura da Funcionalidade

**Diretório**: `apps/inventory/`

### Model - `apps/inventory/models.py`

```python
class StockMovement(models.Model):
    IN = 'IN'
    OUT = 'OUT'
    ADJ = 'ADJ'
    MOVEMENT_TYPES = [
        (IN, 'Entrada'),
        (OUT, 'Saída'),
        (ADJ, 'Ajuste'),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='movements')
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True)
```

**Explicação do Model**:
- **Constantes de tipo**: Define três tipos de movimentação (IN/OUT/ADJ) como constantes para evitar strings mágicas e facilitar manutenção
- **on_delete=PROTECT**: Impede deleção acidental de produtos ou usuários que têm movimentações associadas, preservando integridade referencial
- **related_name**: Permite acesso reverso (`product.movements.all()` e `user.stock_movements.all()`)
- **auto_now_add=True**: Registra automaticamente o timestamp de criação sem intervenção manual

### View - `apps/inventory/views.py`

```python
def form_valid(self, form):
    """
    Sobrescreve o método para associar o usuário e atualizar o estoque
    do produto de forma atômica
    """
    form.instance.user = self.request.user

    with transaction.atomic():
        response = super().form_valid(form)

        movement = self.object
        product = movement.product

        if movement.movement_type == StockMovement.IN:
            product.stock_quantity = F('stock_quantity') + movement.quantity
        elif movement.movement_type == StockMovement.OUT:
            product.stock_quantity = F('stock_quantity') - movement.quantity
        elif movement.movement_type == StockMovement.ADJ:
            product.stock_quantity = F('stock_quantity') + movement.quantity
        
        product.save()
    
    return response
```

**Explicação da View**:
- **form.instance.user**: Associa automaticamente o usuário logado à movimentação, criando trilha de auditoria
- **transaction.atomic()**: Garante que toda a operação (criar movimentação + atualizar estoque) seja executada como transação única - se qualquer parte falhar, tudo é revertido
- **F('stock_quantity')**: Usa expressão F do Django para atualização no nível do banco de dados, evitando race conditions em ambientes concorrentes
- **Lógica condicional**: IN adiciona, OUT subtrai, ADJ pode ser positivo ou negativo dependendo do valor

### Validação - `apps/inventory/forms.py`

```python
def clean(self):
    cleaned_data = super().clean()
    movement_type = cleaned_data.get('movement_type')
    quantity = cleaned_data.get('quantity')
    product = cleaned_data.get('product')

    if movement_type == StockMovement.OUT and quantity <= 0:
        self.add_error('quantity', "Para saídas, a quantidade deve ser positiva.")
    
    if movement_type == StockMovement.IN and quantity <= 0:
        self.add_error('quantity', "Para entradas, a quantidade deve ser positiva.")
    
    if movement_type == StockMovement.OUT:
        if product.stock_quantity < quantity:
            self.add_error('quantity', f"Estoque insuficiente. Quantidade disponível: {product.stock_quantity}.")
```

**Explicação da Validação**:
- **clean()**: Método de validação cross-field, validando múltiplos campos em conjunto
- **Validação de quantidade positiva**: Previne erros lógicos como "entrada de -10 unidades"
- **Validação de estoque suficiente**: Impede que saídas deixem o estoque negativo, mantendo consistência de dados
- **add_error()**: Adiciona mensagens de erro específicas ao campo correspondente para feedback ao usuário

***

<br>

## 2. Sistema de Alertas de Estoque Baixo

### Arquitetura da Funcionalidade

**Diretório**: `apps/products/` e `apps/inventory/`

### Manager Customizado - `apps/products/models.py`

```python
class ProductManager(models.Manager):
    def low_stock(self):
        return self.filter(stock_quantity__lte=models.F('minimum_stock'))
    
    def out_of_stock(self):
        return self.filter(stock_quantity=0)

class Product(models.Model):
    objects = ProductManager()
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.minimum_stock
    
    @property
    def stock_status(self):
        if self.stock_quantity == 0:
            return 'out_of_stock'
        elif self.stock_quantity <= self.minimum_stock:
            return 'low_stock'
        else:
            return 'normal'
```

**Explicação do Manager**:
- **Custom Manager**: Encapsula lógica de negócio complexa em métodos reutilizáveis no ORM
- **F('minimum_stock')**: Compara campos diretamente no banco de dados, mais eficiente que trazer dados para Python
- **@property**: Transforma métodos em atributos computados, simplificando acesso no template
- **stock_status**: Retorna string categorizada para fácil uso em CSS classes e lógica condicional

### View de Alertas - `apps/inventory/views.py`

```python
class StockAlertsView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/stock_alerts.html'
    context_object_name = 'low_stock_products'
    paginate_by = 20

    def get_queryset(self):
        return Product.objects.low_stock().select_related('category').order_by('stock_quantity')
```

**Explicação da View**:
- **LoginRequiredMixin**: Restringe acesso apenas a usuários autenticados
- **low_stock()**: Usa o manager customizado para consulta otimizada
- **select_related('category')**: JOIN SQL para buscar categoria em uma única query, evitando problema N+1
- **order_by('stock_quantity')**: Ordena do mais crítico (menos unidades) para o menos urgente

***

<br>

## 3. Dashboard com Métricas Operacionais

### Arquitetura da Funcionalidade

**Diretório**: `apps/inventory/`

### View Completa - `apps/inventory/views.py`

```python
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_products = Product.objects.count()
        total_suppliers = Supplier.objects.count()
        total_movements = StockMovement.objects.count()

        low_stock_products = Product.objects.low_stock().select_related('category')
        low_stock_count = low_stock_products.count()

        recent_activities = StockMovement.objects.select_related('product', 'user').order_by('-created_at')[:10]

        active_users_count = User.objects.filter(is_active=True).count()

        context.update({
            'total_products': total_products,
            'total_suppliers': total_suppliers,
            'low_stock_count': low_stock_count,
            'low_stock_products': low_stock_products[:5],
            'total_movements': total_movements,
            'recent_activities': recent_activities,
            'active_users': active_users_count,
        })
        return context
```

**Explicação do Dashboard**:
- **TemplateView**: View baseada em classe para renderização simples de template
- **count()**: Executa COUNT SQL diretamente no banco, extremamente eficiente
- **Reutilização de queryset**: `low_stock_products` é usado duas vezes - Django faz cache automático
- **select_related()**: Otimiza queries com JOINs, reduzindo número de consultas ao banco
- **[:10] e [:5]**: Slicing de queryset limitado no SQL (LIMIT 10), não traz dados desnecessários
- **context.update()**: Adiciona múltiplas variáveis ao contexto de uma vez

***

<br>

## 4. Geração de Relatórios com Exportação CSV

### Arquitetura da Funcionalidade

**Diretório**: `apps/reports/`

### Relatório de Estoque - `apps/reports/views.py`

```python
class StockReportView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'reports/stock_report.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = Product.objects.select_related('category').annotate(
            total_value=ExpressionWrapper(
                F('stock_quantity') * F('price'),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        ).only(
            'id', 'name', 'sku', 'stock_quantity', 'minimum_stock', 'price',
            'category__name'
        ).order_by('name')

        status = self.request.GET.get('status')
        if status == 'low':
            queryset = queryset.filter(stock_quantity__lte=F('minimum_stock'))
        elif status == 'out':
            queryset = queryset.filter(stock_quantity=0)
        elif status == 'ok':
            queryset = queryset.filter(stock_quantity__gt=F('minimum_stock'))

        return queryset
```

**Explicação do Relatório**:
- **annotate()**: Adiciona campo computado ao queryset, calculado no banco de dados
- **ExpressionWrapper**: Necessário para operações aritméticas que precisam especificar output_field
- **F('stock_quantity') * F('price')**: Cálculo no SQL, muito mais rápido que em Python
- **only()**: Limita campos retornados (SELECT específico), reduzindo tamanho da resposta
- **Filtros dinâmicos**: Aplica filtros condicionalmente baseado em parâmetros GET

### Exportação CSV - `apps/reports/views.py`

```python
def export_stock_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="relatorio_estoque.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Produto', 'SKU', 'Categoria',
        'Estoque Atual', 'Estoque Mínimo',
        'Preço Unit.', 'Valor Total', 'Status'
    ])

    products = Product.objects.select_related('category').annotate(
        total_value=ExpressionWrapper(
            F('stock_quantity') * F('price'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )

    for product in products:
        if product.stock_quantity == 0:
            status = 'Sem Estoque'
        elif product.stock_quantity <= product.minimum_stock:
            status = 'Estoque Baixo'
        else:
            status = 'Normal'
        
        writer.writerow([
            product.name,
            product.sku,
            product.category.name,
            product.stock_quantity,
            product.minimum_stock,
            f'{product.price:.2f}',
            f'{product.total_value:.2f}',
            status,
        ])

    return response
```

**Explicação da Exportação**:
- **HttpResponse com content_type CSV**: Retorna arquivo CSV diretamente sem template
- **Content-Disposition attachment**: Força download do arquivo no navegador
- **charset=utf-8**: Garante suporte correto a acentuação e caracteres especiais
- **csv.writer**: Biblioteca padrão Python para manipulação CSV com escape automático
- **f-strings com formatação**: `.2f` garante duas casas decimais para valores monetários
- **Lógica de status**: Calcula status visualmente claro para análise externa

***

<br>

## 5. Sistema de Busca Avançada com Autocomplete

### Arquitetura da Funcionalidade

**Diretório**: `apps/products/`

### Autocomplete API - `apps/products/views.py`

```python
@method_decorator(ratelimit(key='ip', rate='30/m', method='GET'), name='dispatch')
@method_decorator(cache_page(60 * 5), name='dispatch')
class ProductAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()

        if len(query) < 2:
            return JsonResponse({'results': []})
        
        logger.info(f"Autocomplete search: query='{query}' ip={request.META.get('REMOTE_ADDR')}")
        
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(description__icontains=query)
        ).select_related('category').only(
            'id', 'name', 'sku', 'stock_quantity', 'price', 'category__name'
        ).order_by('name')[:10]

        results = [
            {
                'id': p.id,
                'name': p.name,
                'sku': p.sku,
                'category': p.category.name if p.category else 'Sem categoria',
                'stock': p.stock_quantity,
                'price': float(p.price),
                'url': f'/products/{p.id}/',
            }
            for p in products
        ]

        return JsonResponse({
            'results': results,
            'count': len(results),
            'query': query
        })
```

**Explicação do Autocomplete**:
- **@ratelimit**: Limita 30 requisições por minuto por IP, proteção contra abuse/DDoS
- **@cache_page(60 * 5)**: Cache de 5 minutos, reduz carga no banco para buscas repetidas
- **len(query) < 2**: Retorna vazio para queries curtas, evita sobrecarga com pesquisas genéricas
- **Q objects com OR**: Busca em múltiplos campos simultaneamente (nome OU SKU OU descrição)
- **__icontains**: Busca case-insensitive com LIKE %query% no SQL
- **[:10]**: Limita resultados para performance e UX (não sobrecarregar interface)
- **JsonResponse**: Retorna JSON estruturado para consumo por JavaScript frontend
- **logger.info**: Registra buscas para análise de comportamento e debugging

### Widget Select2 - `apps/inventory/forms.py`

```python
from django_select2.forms import ModelSelect2Widget

class ProductWidget(ModelSelect2Widget):
    search_fields = [
        'name__icontains',
        'sku__icontains',
    ]

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'reason']
        widgets = {
            'product': ProductWidget(
                attrs={'data-placeholder': 'Digite o nome ou SKU do produto...'}
            ),
        }
```

**Explicação do Widget**:
- **ModelSelect2Widget**: Widget Django que integra biblioteca Select2.js para autocomplete
- **search_fields**: Define quais campos do modelo podem ser pesquisados via AJAX
- **attrs**: Adiciona atributos HTML customizados ao widget
- **data-placeholder**: Melhora UX com texto explicativo no campo vazio

***

<br>

## 6. Sistema de Controle de Acesso RBAC

### Arquitetura da Funcionalidade

**Diretório**: `apps/accounts/`

### Model de Perfil - `apps/accounts/models.py`

```python
class Profile(models.Model):
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    STAFF = 'STAFF'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (STAFF, 'Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STAFF)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
```

**Explicação do Model**:
- **OneToOneField**: Relacionamento 1:1 com User - cada usuário tem exatamente um perfil
- **on_delete=CASCADE**: Quando usuário é deletado, perfil também é removido automaticamente
- **ROLE_CHOICES**: Lista de tuplas para dropdown no admin e forms
- **default=STAFF**: Novos usuários começam com permissões mínimas (princípio de menor privilégio)
- **blank=True, null=True**: Campos opcionais para informações adicionais

### Mixins de Permissão - `apps/accounts/mixins.py`

```python
class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []
    redirect_url = reverse_lazy('inventory:dashboard')
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        if self.request.user.is_superuser:
            return True
        
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role in self.allowed_roles
        
        return False
    
    def handle_no_permission(self):
        messages.error(
            self.request,
            'Voce nao tem permissao para acessar esta pagina.'
        )
        return redirect(self.redirect_url)

class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN']

class ManagerOrAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN', 'MANAGER']
```

**Explicação dos Mixins**:
- **UserPassesTestMixin**: Mixin do Django para autorização baseada em lógica customizada
- **test_func()**: Define a lógica de permissão - retorna True se usuário pode acessar
- **is_superuser**: Superusuário sempre tem acesso (bypass para manutenção)
- **hasattr**: Verifica se perfil existe antes de acessar (previne AttributeError)
- **handle_no_permission()**: Customiza comportamento quando acesso negado
- **Herança de mixins**: Classes específicas herdam lógica base, apenas definindo roles permitidos

### Aplicação em Views - `apps/products/views.py`

```python
class ProductCreateView(ManagerOrAdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')
    success_message = 'Produto criado com sucesso.'

class ProductDeleteView(AdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    success_message = 'Produto excluído com sucesso.'
```

**Explicação da Aplicação**:
- **Ordem dos Mixins**: Ordem importa - primeiro verificações de permissão, depois login
- **Multiple inheritance**: Django resolve MRO (Method Resolution Order) da esquerda para direita
- **Granularidade**: Criar produto requer MANAGER+, deletar requer apenas ADMIN
- **Composição declarativa**: Sem lógica no método, apenas declaração de requisitos

***

<br>

## 7. Proteção de Deleção com Validação de Integridade

### Arquitetura da Funcionalidade

**Diretório**: `apps/products/`

### View de Exclusão Protegida - `apps/products/views.py`

```python
class ProductDeleteView(AdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            self.object.delete()
            messages.success(request, self.success_message)
            return redirect(self.get_success_url())
        
        except ProtectedError:
            error_message = (
                f'O produto "{self.object.name}" não pode ser excluído. '
                'Ele possui um histórico de movemntações de estoque associado. '
                'Para removê-lo, considere desativá-lo ou arquivá-lo.'
            )
            messages.error(request, error_message)
            return redirect('products:product_list')
```

**Explicação da Proteção**:
- **try/except ProtectedError**: Captura exceção específica do Django para ForeignKey protegida
- **Mensagem amigável**: Explica ao usuário POR QUE não pode deletar e sugere alternativa
- **Não silencia erro**: Informa claramente o bloqueio, transparente ao usuário
- **Redirect apropriado**: Volta para lista em vez de mostrar tela de confirmação

### Configuração no Model - `apps/inventory/models.py`

```python
class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='movements')
```

**Explicação do PROTECT**:
- **on_delete=PROTECT**: Bloqueia deleção do produto se houver movimentações associadas
- **Integridade referencial**: Previne orphan records e perda de histórico
- **Alternativas**: CASCADE deletaria movimentações (perda de dados), SET_NULL criaria inconsistência

***

<br>

## 8. Relatório de Usuários (Admin)

### Arquitetura da Funcionalidade

**Diretório**: `apps/reports/`

### View Completa - `apps/reports/views.py`

```python
class UserReportView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'reports/user_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = total_users - active_users

        users_by_role = {
            'ADMIN': Profile.objects.filter(role='ADMIN', user__is_active=True).count(),
            'MANAGER': Profile.objects.filter(role='MANAGER', user__is_active=True).count(),
            'STAFF': Profile.objects.filter(role='STAFF', user__is_active=True).count(),
        }

        last_30_days = timezone.now() - timedelta(days=30)
        new_users_30d = User.objects.filter(date_joined__gte=last_30_days).count()

        recent_users = User.objects.select_related('profile').order_by('-date_joined')[:10]

        context.update({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'users_by_role': users_by_role,
            'new_users_30d': new_users_30d,
            'recent_users': recent_users,
            'page_title': 'Relatório de Usuários e Acessos',
        })

        return context
```

**Explicação do Relatório de Usuários**:
- **AdminRequiredMixin**: Apenas ADMIN pode ver dados sensíveis de usuários
- **Métricas agregadas**: Fornece visão estatística sem expor dados individuais sensíveis
- **users_by_role**: Dicionário facilita iteração no template e gráficos
- **timezone.now()**: Usa timezone-aware datetime para consistência em ambientes distribuídos
- **timedelta**: Cálculo de datas relativas de forma legível e manutenível
- **select_related('profile')**: Otimização para evitar N+1 queries ao listar usuários recentes

***

<br>

## Padrões Arquiteturais Aplicados

### Performance
- **select_related()**: JOINs SQL para relacionamentos ForeignKey/OneToOne
- **only()**: Limita campos retornados (SELECT específico)
- **F expressions**: Operações no banco de dados em vez de Python
- **Cache**: Reduce consultas repetidas ao banco

### Segurança
- **transaction.atomic()**: Garante consistência ACID
- **PROTECT**: Previne deleção acidental de dados relacionados
- **RBAC**: Controle granular de acesso por função
- **Rate limiting**: Proteção contra abuse de APIs

### Usabilidade
- **Autocomplete**: UX moderna para grandes datasets
- **Mensagens informativas**: Feedback claro sobre operações
- **Validação server-side**: Previne dados inválidos mesmo com JavaScript desabilitado

Todas as funcionalidades seguem princípios SOLID e padrões Django para manutenibilidade e escalabilidade.
