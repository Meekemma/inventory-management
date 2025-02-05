from django.contrib import admin
from .models import LowStockAlert

# Register your models here.



@admin.register(LowStockAlert)
class LowStockAlertAdmin(admin.ModelAdmin):
    list_display = ('product', 'threshold', 'is_alerted')
    list_filter = ('is_alerted',)
    search_fields = ('product__name',)






