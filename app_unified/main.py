import httpx
from typing import Any, Dict

from enum import Enum 
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError

#1 Enum for supported symbols:

class Symbol(str, Enum):
    BTC = "bitcoin"     
    ETH = "ethereum"   
    XRP = "ripple"    

class Currency(str, Enum):
    USD = "usd"     
    EUR = "eur"   
    GBP = "gbp" 
    AUD = "aud"
    CHF = "chf"
    JPY = "jpy" 

class MarketChartParams(BaseModel):
    symbol: Symbol
    currency: Currency
    days: int = Field(gt=0, description="Number of days must be greater than 0")


def fetch_market_chart_2_business(symbol: Symbol, currency: Currency, days: int)-> Dict[str, Any]:    
    '''
    Business logic layer for fetching CoinGecko market charts.
    Steps:
    - Validate parameters with Pydantic
    - Call the HTTP client
    - Do minimal validation of the response
    '''

    # 1) Validate entry parameters with Pydantic
    params = MarketChartParams(symbol=symbol, currency=currency, days=days)
    
    # 2) Call HTTP client
    data = get_market_chart_http_3(params.symbol.value, params.currency.value, params.days)    
    
    # 3 ) Minimal validation of structure of response
    if "prices" not in data:
        raise RuntimeError("Unexpected CoinGecko format: missing 'prices'")
    
    return data #RAW JSON
#----------------------------------------------------------------#


def get_market_chart_http_3(coin: str, currency: str, days: int) -> Dict[str, Any]:
    """Call CoinGecko /market_chart and return the JSON payload.

    Example:
        get_market_chart("bitcoin", "usd", 7) -> dict with "prices", "market_caps", ...
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {
        "vs_currency": currency,
        "days": days,
    }

    try:
        response = httpx.get(url, params=params, timeout=5.0)
    except httpx.TimeoutException as exc:
        # Timeouts: the server took too long to respond
        raise RuntimeError(f"Timeout while requesting {url}") from exc
    except httpx.RequestError as exc:
        # Network errors: DNS, connection refused, etc.
        raise RuntimeError(f"Network error while requesting {exc.request.url!r}") from exc

    if response.status_code != 200:
        # Non-200: we do NOT try to parse JSON, we just raise with context
        raise RuntimeError(
            f"CoinGecko API error {response.status_code} for URL: {url}\n"
            f"Response body: {response.text[:200]}"
        )

    try:
        return response.json()
    except ValueError as exc:
        # 200 OK but invalid JSON (rare, but we handle it)
        raise RuntimeError(
            f"Failed to parse JSON from CoinGecko for URL: {url}\n"
            f"Raw body: {response.text[:200]}"
        ) from exc



#--------------------------------FAST API LAYER--------------------------------#

from fastapi import FastAPI, HTTPException

app_unified = FastAPI(title="CoinGecko Market Chart API", version="1.0.0")

@app_unified.get('/market_chart')
def get_market_chart_endpoint(
    symbol: Symbol, 
    currency: Currency, 
    days: int):
    """
    HTTP endpoint that exposes fetch_market_chart_2 via FastAPI.

    Query params:
    - symbol: BTC, ETH, XRP
    - currency: USD, EUR, GBP, AUD, CHF, JPY
    - days: int > 0
    """
    try:
        data = fetch_market_chart_2_business(symbol, currency, days)
        return data
    except ValidationError as e:
        #Problem with params (days <=0, invalid symbol, etc)        
        #return 422 Unprocessable Entity with details
        raise HTTPException(status_code=422, detail=e.errors())
    except RuntimeError as e:
        #Problem with HTTP client or response, network, etc
        raise HTTPException(status_code=502, detail=str(e))    









if __name__ == "__main__":
    data = fetch_market_chart_2_business(Symbol.BTC, Currency.EUR, 7) 
    print(len(data["prices"]))
    print(data["prices"][:10])