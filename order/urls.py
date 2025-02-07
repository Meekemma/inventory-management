from django.urls import path
from . import views

urlpatterns = [
     
    path('create_order/', views.create_order, name='create_order'), 
    path('track_status/', views.track_status, name='track_status'),
    path('status_update/<int:order_id>/', views.status_update, name='status_update'),  
    path('order_update/<int:order_item_id>/', views.update_order_item, name='order_update'),

]
