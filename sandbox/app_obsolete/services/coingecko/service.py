#the brain

# app/services/coingecko/service.py

from app.services.coingecko.client import get_market_chart 
from app.models.coingecko import SYMBOL_MAP, CURRENCY_MAP

def fetch_market_chart(symbol: str, currency: str, days: int):
    """Business logic layer for fetching CoinGecko market charts."""

    # 1) Validate symbol
    symbol = symbol.upper()
    if symbol not in SYMBOL_MAP:
        raise ValueError(f"Unsupported symbol: {symbol}")

    # 2) Convert symbol -> CoinGecko ID
    coin_id = SYMBOL_MAP[symbol]

    # 3) Validate days
    if days <= 0: 
        raise ValueError("Days must be > 0") 
    
    #Validate currency
    currency = currency.upper()
    if currency not in CURRENCY_MAP:
        raise ValueError(f"Unsupported currency: {currency}")

    # 4) Call the client
    data = get_market_chart(coin_id, currency, days)

    # 5) Minimal validation of structure of response
    if "prices" not in data:
        raise RuntimeError("Unexpected CoinGecko format: missing 'prices'")

    return data   # JSON CRUDO (no DF aquí!)

#Test:
if __name__ == "__main__":
    print(fetch_market_chart("BTC", "EUR", 50))
    