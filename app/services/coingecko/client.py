import httpx
from typing import Any, Dict



def get_market_chart(coin: str, currency: str, days: int) -> Dict[str, Any]:
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


#ideal no error code (without raise, exception or try)
import httpx
from typing import Any, Dict
def get_market_chart_ideal(coin: str, currency: str, days: int) -> Dict[str, Any]:    
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    paramss = {"vs_currency": currency,"days": days}
    response = httpx.get(url, params=paramss, timeout=5.0)
    if response.status_code != 200:
        return {}
    return response.json()