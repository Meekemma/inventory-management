from django.urls import path
from . import views

urlpatterns = [
    path('create_purchase_order/', views.create_purchase_order, name='create_purchase_order'),
    path('track_order_status/', views.track_order_status, name='track_order_status'),
    path('order_status_update/<int:order_id>/', views.order_status_update, name='order_status_update'), 

]

