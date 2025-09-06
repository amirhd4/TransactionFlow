from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal

CURRENCY_CHOICES = [
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
]

TRANSACTION_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('COMPLETED', 'Completed'),
    ('FAILED', 'Failed'),
]


class Account(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    is_gateway = models.BooleanField(default=False, help_text="Is this account a gateway for fund distribution?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.username} - {self.balance} {self.currency}"

    class Meta:
        # Each user can only have one account per currency
        unique_together = ('owner', 'currency')


class Transaction(models.Model):
    source_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='sent_transactions')
    destination_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='received_transactions')

    amount_sent = models.DecimalField(max_digits=12, decimal_places=2)
    amount_received = models.DecimalField(max_digits=12, decimal_places=2)

    exchange_rate = models.DecimalField(max_digits=18, decimal_places=8)
    fee = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.source_account} to {self.destination_account} - {self.amount_sent} {self.source_account.currency}"


class DistributionRule(models.Model):
    gateway_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='distribution_rules',
                                        limit_choices_to={'is_gateway': True})
    destination_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='distribution_incomes')
    percentage = models.DecimalField(max_digits=5, decimal_places=2,
                                     help_text="Percentage of the income to be distributed (e.g., 40.00 for 40%)")

    def __str__(self):
        return f"{self.percentage}% of {self.gateway_account.owner.username}'s gateway income to {self.destination_account}"

    def clean(self):
        if self.gateway_account == self.destination_account:
            raise ValidationError("Gateway account and destination account cannot be the same.")