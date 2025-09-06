from rest_framework import serializers
from .models import Account, Transaction

class AccountSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    class Meta:
        model = Account
        fields = ['id', 'owner', 'balance', 'currency']

class TransactionCreateSerializer(serializers.Serializer):
    source_account_id = serializers.IntegerField()
    gateway_account_id = serializers.IntegerField()
    amount = serializers.CharField(max_length=20)

class TransactionDetailSerializer(serializers.ModelSerializer):
    source_account = AccountSerializer()
    destination_account = AccountSerializer()
    class Meta:
        model = Transaction
        fields = '__all__'