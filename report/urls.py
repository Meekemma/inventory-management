from django.urls import path
from . import views



urlpatterns = [
    path('low_stock/', views.low_stock_products, name='low_stock_products'),
    path('low_stock_alerts/', views.low_stock_alerts, name='low_stock_alerts'),
    path('sales_report/', views.sales_report, name='sales_report')

]