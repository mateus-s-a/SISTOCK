from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product

User = get_user_model()

# Create your models here.

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

    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['-created_at'], name='movement_created_idx'),
            models.Index(fields=['movement_type'], name='movement_type_idx'),
            models.Index(fields=['product', '-created_at'], name='movement_product_created_idx'),
        ]
    
    def get_movement_type_display(self):
        return dict(self.MOVEMENT_TYPES).get(self.movement_type, 'Desconhecido')
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product} - {self.quantity}"
    