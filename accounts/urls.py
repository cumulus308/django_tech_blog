from django.urls import path
from .views import CustomLoginView, SignUpView, index
from django.contrib.auth import views as auth_views
app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', SignUpView.as_view(), name='signup'),
]