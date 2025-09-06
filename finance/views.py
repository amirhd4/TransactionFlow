from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal, InvalidOperation

from .serializers import TransactionCreateSerializer, TransactionDetailSerializer
from django.shortcuts import render
from django.views.generic import TemplateView

from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Account
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import TransactionForm
from .services import execute_financial_transaction, TransactionError


class CreateTransactionView(LoginRequiredMixin, FormView):
    form_class = TransactionForm
    template_name = 'create_transaction.html'
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            transaction = execute_financial_transaction(
                source_account_id=form.cleaned_data['source_account'].id,
                gateway_account_id=form.cleaned_data['gateway_account'].id,
                amount_sent=form.cleaned_data['amount'],
                initiator_user=self.request.user
            )
            messages.success(self.request, f"Transaction successful! ID: {transaction.id}")
        except (TransactionError, ConnectionError, ValueError) as e:
            messages.error(self.request, f"Transaction failed: {e}")

        return redirect(self.success_url)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = Account.objects.filter(owner=self.request.user)
        return context


class HomeView(TemplateView):
    template_name = "home.html"


class CreateTransactionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = TransactionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        try:
            amount_decimal = Decimal(validated_data['amount'])
            if amount_decimal <= 0:
                raise ValueError("Amount must be positive.")
        except (InvalidOperation, ValueError) as e:
            return Response({'error': f'Invalid amount provided. {e}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction = execute_financial_transaction(
                source_account_id=validated_data['source_account_id'],
                gateway_account_id=validated_data['gateway_account_id'],
                amount_sent=amount_decimal,
                initiator_user=request.user
            )

            response_serializer = TransactionDetailSerializer(transaction)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except TransactionError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except (ConnectionError, ValueError) as e:
            return Response({"error": f"External service error: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            return Response({"error": "An unexpected server error occurred."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)