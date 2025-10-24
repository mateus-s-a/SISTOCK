from django.contrib import admin
from .models import Supplier

# Register your models here.

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    search_fields = ["name", "cnpj", "email"]
    list_display = ["name", "contact_person", "email", "phone", "cnpj"]