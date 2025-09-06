import requests
from decimal import Decimal
from django.conf import settings
from decouple import config


API_BASE_URL = "https://v6.exchangerate-api.com/v6"
API_KEY = config('EXCHANGERATE_API_KEY')

def get_exchange_rate(source_currency: str, target_currency: str) -> Decimal:
    """
    Fetches the exchange rate between two currencies.
    Returns the rate to multiply with source_currency to get target_currency.
    e.g., if USD to EUR is 0.93, it returns Decimal('0.93').
    """
    if source_currency == target_currency:
        return Decimal("1.0")

    try:
        url = f"{API_BASE_URL}/{API_KEY}/latest/{source_currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data.get("result") == "success":
            rate = data["conversion_rates"].get(target_currency)
            if rate is None:
                raise ValueError(f"Target currency '{target_currency}' not found in API response.")
            return Decimal(str(rate))
        else:
            raise ConnectionError(f"ExchangeRate API error: {data.get('error-type')}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not connect to exchange rate service: {e}")
    except (ValueError, KeyError) as e:
        raise ValueError(f"Could not parse exchange rate data: {e}")