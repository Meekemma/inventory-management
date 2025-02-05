from django.urls import path
from . import views
from .views import MyTokenObtainPairView


from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('registration/', views.registration_view, name='registration'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('logout/', views.logout_view, name='logout'),
    

]

