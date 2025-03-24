from django.urls import path
from . import views

urlpatterns = [
    path('orders/create/', views.create_order, name='create_order'),
    # Retrieve all orders for the authenticated user
    path('orders/', views.get_user_orders, name='get_user_orders'),
    # Retrieve, update, or delete a specific order by ID
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    # Update an order item by ID
    path('order-items/<int:order_item_id>/', views.update_order_item, name='update_order_item'),
    path('track_status/', views.track_status, name='track_status'),
    path('status_update/<int:order_id>/', views.status_update, name='status_update'),  
    path('order_update/<int:order_item_id>/', views.update_order_item, name='order_update'),

]
