# finance/urls.py
from django.urls import path
from .views import DashboardView, CreateTransactionView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('transaction/new/', CreateTransactionView.as_view(), name='create_transaction'),
]