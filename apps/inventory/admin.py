from django.contrib import admin
from .models import StockMovement

# Register your models here.

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["product", "movement_type", "quantity", "user", "created_at"]
    list_filter = ["movement_type", "created_at", "product__category", "user"]
    search_fields = ["product__name", "product__sku", "user__username"]