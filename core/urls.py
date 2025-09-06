# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # Import auth views

from finance.views import HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),

    # Add login and logout URLs
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Include our finance app's URLs (we will create this file next)
    path('', include('finance.urls')),

    # We can now remove the API and JWT urls as we are not using them for the UI
    # path('api/finance/', include('finance.urls')),
    # path('api/token/', ...),
]