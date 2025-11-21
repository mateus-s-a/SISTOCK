from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
    
    def __str__(self):
        return self.name


class ProductManager(models.Manager):
    def low_stock(self):
        return self.filter(stock_quantity__lte=models.F('minimum_stock'))
    
    def out_of_stock(self):
        return self.filter(stock_quantity=0)


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["name"]
        indexes = [
            models.Index(fields=['sku'], name='product_sku_idx'),
            models.Index(fields=['name'], name='product_name_idx'),
            models.Index(fields=['stock_quantity'], name='product_stock_idx'),
            models.Index(fields=['-created_at'], name='product_created_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def is_low_stock(self):
        # Propriedade retorna True se produto estiver com estoque baixo
        return self.stock_quantity <= self.minimum_stock
    
    @property
    def stock_status(self):
        # Retorna o status do estoque do produto
        if self.stock_quantity == 0:
            return 'out_of_stock'   # <- sem estoque
        elif self.stock_quantity <= self.minimum_stock:
            return 'low_stock'      # <- estoque baixo
        else:
            return 'normal'         # <- com estoque normalizado
    