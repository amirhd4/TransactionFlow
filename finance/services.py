from decimal import Decimal
from django.db import transaction, models
from .models import Account, Transaction, DistributionRule
from .utils import get_exchange_rate


TRANSACTION_FEE_PERCENTAGE = Decimal("2.0")


class TransactionError(Exception):
    """Custom exception for transaction failures."""
    pass


@transaction.atomic
def execute_financial_transaction(
        source_account_id: int,
        gateway_account_id: int,
        amount_sent: Decimal,
        initiator_user
) -> Transaction:
    """
    Executes a complete financial transaction with currency conversion,
    fees, and dynamic fund distribution.
    This function is atomic: all operations succeed or all are rolled back.
    """

    try:
        source_account = Account.objects.select_for_update().get(id=source_account_id)
        gateway_account = Account.objects.select_for_update().get(id=gateway_account_id)
    except Account.DoesNotExist:
        raise TransactionError("Source or Gateway account does not exist.")

    if source_account.owner != initiator_user:
        raise TransactionError("Permission denied: You do not own the source account.")

    if not gateway_account.is_gateway:
        raise TransactionError("Destination account is not a valid gateway.")

    if source_account.id == gateway_account.id:
        raise TransactionError("Source and Gateway accounts cannot be the same.")

    if source_account.balance < amount_sent:
        raise TransactionError("Insufficient funds.")

    fee_amount = (amount_sent * TRANSACTION_FEE_PERCENTAGE) / 100
    amount_to_convert = amount_sent - fee_amount

    if amount_to_convert <= 0:
        raise TransactionError("Amount after fee is zero or less.")

    exchange_rate = get_exchange_rate(source_account.currency, gateway_account.currency)
    final_amount_received_in_gateway_currency = (amount_to_convert * exchange_rate).quantize(Decimal('0.01'))

    source_account.balance -= amount_sent
    source_account.save()

    main_transaction = Transaction.objects.create(
        source_account=source_account,
        destination_account=gateway_account,
        amount_sent=amount_sent,
        amount_received=final_amount_received_in_gateway_currency,
        exchange_rate=exchange_rate,
        fee=fee_amount,
        status='COMPLETED'  # Because this function is atomic, it's either completed or fails entirely
    )

    rules = gateway_account.distribution_rules.all()
    if not rules.exists():
        raise TransactionError("Gateway account has no distribution rules configured.")

    total_percentage = sum(rule.percentage for rule in rules)
    if total_percentage != Decimal("100.00"):
        raise TransactionError(
            f"Distribution rule percentages for this gateway do not sum to 100%. Current sum: {total_percentage}%")

    for rule in rules:
        destination = rule.destination_account
        share_percentage = rule.percentage

        destination_account = Account.objects.select_for_update().get(id=destination.id)

        if destination_account.currency != gateway_account.currency:
            raise TransactionError(
                f"Distribution account {destination_account.id} has a different currency than the gateway.")

        distributed_amount = (final_amount_received_in_gateway_currency * share_percentage) / 100

        destination_account.balance += distributed_amount.quantize(Decimal('0.01'))
        destination_account.save()

    return main_transaction