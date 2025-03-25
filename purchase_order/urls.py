from django.urls import path
from . import views

urlpatterns = [
    path('create_purchase_order/', views.create_purchase_order, name='create_purchase_order'),
    path('track_order_status/', views.track_order_status, name='track_order_status'),
    path('order_status_update/<int:order_id>/', views.order_status_update, name='order_status_update'),
    path('<int:order_id>/', views.get_purchase_order, name='get_purchase_order'),
    path('<int:order_id>/items/', views.manage_purchase_order_item, name='create_purchase_order_item'),  # POST
    path('<int:order_id>/items/<int:item_id>/', views.manage_purchase_order_item, name='manage_purchase_order_item'),  # PUT, DELETE
    path('<int:order_id>/delete/', views.delete_purchase_order, name='delete_purchase_order'),
]

