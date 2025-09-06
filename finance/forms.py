from django import forms
from .models import Account

class TransactionForm(forms.Form):
    source_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        label="From Account",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    gateway_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_gateway=True),
        label="To Gateway",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show accounts owned by the current user
            self.fields['source_account'].queryset = Account.objects.filter(owner=user, is_gateway=False)