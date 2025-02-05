from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.categories, name='categories'),
    path('create_category/', views.create_category, name='create_category'),
    path('update_category/<int:pk>/', views.update_category, name='update_category'),
    path('products/', views.products, name='products'),
    path('create_products/', views.create_products, name='create_products'),
    path('update_products/<int:pk>/', views.update_products, name='update_products'),
    path('create_transaction/', views.create_transaction, name='create_transaction'),
    path('transaction_history/', views.transaction_history, name='transaction_history'),

    path('suppliers/', views.suppliers, name='suppliers'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    
]



