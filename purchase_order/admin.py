from django.contrib import admin
from .models import  PurchaseOrder, PurchaseOrderItem

# Register your models here.


@admin.register(PurchaseOrder)
class PurchaseOrder(admin.ModelAdmin):
    list_display = ('id', 'user','supplier','total_price', 'ordered_date', 'status', 'is_paid', 'received')
    search_fields = ('id', 'status')
    list_filter = ('status', 'ordered_date')
    ordering = ['-ordered_date'] 



@admin.register(PurchaseOrderItem)
class PurchaseOrderItem(admin.ModelAdmin):
    list_display = ( 'id','order', 'product', 'quantity','date_added')
    search_fields = ('order__id', 'product__name')
    list_filter = ('date_added', 'product')

