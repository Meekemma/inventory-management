from django.contrib import admin
from .models import Category, Product, InventoryTransaction, Supplier



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created_at')
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_name', 'phone','email', 'address', 'created_at')
    list_filter = ('name','contact_name')
    search_fields = ('name', 'contact_name')




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'sku','category', 'supplier','quantity', 'price', 'cost_price', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')



@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity', 'created_at')
    list_filter = ('transaction_type',)
    search_fields = ('product__name',)



