from django.urls import path
from . import views


from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path('registration/', views.registration_view, name='registration'),
    path('login/', views.login_view, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change_password/', views.change_password_view, name='change_password'),
    path('logout/', views.logout_view, name='logout'),

]