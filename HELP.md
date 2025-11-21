# Working Windows 10
- Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
- venv\Scripts\activate
- uvicorn app.api.main:app --reload

# Current point
1.Vertical use case working (Api-Domain-Infrastructure):
    - /api/v1/market_chart/?symbol=ripple&currency=usd&days=30&provider=coingecko

## Next Steps
1. Build analytics on top with pandas + plotly (later)
    a) /market_chart/stats: Compute: min, max, mean, median, std, first_price, last_price, % change