from django.contrib import admin
from .models import Category, Product

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "description"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ["name", "sku"]
    list_display = ["name", "sku", "category", "price", "stock_quantity", "minimum_stock"]
    list_filter = ["category"]
