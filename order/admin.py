from django.contrib import admin
from .models import  Order, OrderItem

# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'ordered_date', 'status', 'is_paid')
    search_fields = ('id', 'status')
    list_filter = ('status', 'ordered_date')
    ordering = ['-ordered_date'] 



@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ( 'id','order', 'product', 'quantity','date_added')
    search_fields = ('order__id', 'product__name')
    list_filter = ('date_added', 'product')

