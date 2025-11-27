# tests/test_api_market_chart.py

from datetime import datetime, timedelta
import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.market_chart import router as market_chart_router
from app.domain.entities import Symbol, Currency, Provider, PricePoint, MarketChartData
from app.domain import errors as domain_errors

from app.api.routes import market_chart as api_market_chart

#Test the dataframe endpoints of the market_chart router
# We will mock the domain service functions to return controlled data
app = FastAPI()
app.include_router(market_chart_router)
client = TestClient(app)

# --- Helpers -----------------------------------------------------------------

# Deterministic MarketChartData for testing.
def _build_fake_marketchartdata(days: int = 10) -> MarketChartData:
    """
    Deterministic MarketChartData for testing.
    timestamp: 2023-01-01 + i days
    price: 100 + 10 * i
    """
    base_ts = datetime(2023, 1, 1)
    points: list[PricePoint] = []
    for i in range(days):
        points.append(
            PricePoint(
                timestamp=base_ts + timedelta(days=i),
                price=float(100 + 10 * i),
            )
        )
    return MarketChartData(Symbol.BTC, Currency.USD, points)

# Fake fetch_market_chart to return deterministic data
def _fake_fetch_market_chart(symbol, currency, days, provider) -> MarketChartData:
    # Ignore parameters and just return deterministic data
    return _build_fake_marketchartdata(days=days)   

# --- Tests -------------------------------------------------------------------

# Test the /market_chart/ endpoint
def test_get_market_chart_success(monkeypatch):
    # Patch fetch_market_chart to return fake data
    monkeypatch.setattr(api_market_chart,"fetch_market_chart",_fake_fetch_market_chart)

    # Make the API call
    response = client.get(
        "/market_chart/",
        params={
            "symbol": 'bitcoin',
            "currency": 'usd',
            "days": 5,
            "provider": 'coingecko',
        }
    )
    # Check the response
    assert response.status_code == 200
    data = response.json()
    
    assert data["symbol"] == "bitcoin"
    assert data["currency"] == "usd"
    assert len(data["points"]) == 5
    for i, point in enumerate(data["points"]):
        expected_price = 100 + 10 * i
        assert point["price"] == expected_price


# Test error handling for BusinessNoDataError
def test_get_market_chart_no_data_error(monkeypatch):
    # Patch fetch_market_chart to raise BusinessNoDataError
    def _raise_no_data_error(symbol, currency, days, provider):
        raise domain_errors.BusinessNoDataError("No data available for the given parameters.")
    
    monkeypatch.setattr(api_market_chart,"fetch_market_chart",_raise_no_data_error)

    # Make the API call
    response = client.get(
        "/market_chart/",
        params={
            "symbol": 'bitcoin',
            "currency": 'usd',
            "days": 5,
            "provider": 'coingecko',
        }
    )
    # Check the response
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No data available for the given parameters."
    
# Test the /market_chart/stats endpoint
def test_get_market_chart_stats_success(monkeypatch):
    # Patch compute_market_chart_stats to return fake stats
    '''
    class StatsResponse(BaseModel):
        count: int
        min_price: float
        max_price: float
        mean_price: float
        median_price: float
        std_dev: float
        variance: float
        first_price: float
        last_price: float
        percent_change: float

        @classmethod
        def from_dict(cls, dict_stats: dict) -> 'StatsResponse':
            return cls(**dict_stats) #cleaner and professional way to do it
    '''
    def _fake_compute_market_chart_stats(symbol, currency, days, provider) -> dict:
        return {
            "count": days,
            "min_price": 100.0,
            "max_price": 100.0 + 10.0 * (days - 1),
            "mean_price": 100.0 + 5.0 * (days - 1),
            "median_price": 100.0 + 5.0 * (days - 1),
            "std_dev": 14.43,
            "variance": 208.33,
            "first_price": 100.0,
            "last_price": 100.0 + 10.0 * (days - 1),
            "percent_change": ((100.0 + 10.0 * (days - 1)) - 100.0) / 100.0 * 100,
        }
    monkeypatch.setattr(api_market_chart,"compute_market_chart_stats",_fake_compute_market_chart_stats)
    # Make the API call
    response = client.get(
        "/market_chart/stats",
        params={
            "symbol": 'bitcoin',
            "currency": 'usd',
            "days": 5,
            "provider": 'coingecko',
        }
    )
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5
    assert data["min_price"] == 100.0
    assert data["max_price"] == 140.0
    assert data["mean_price"] == 120.0
    assert data["median_price"] == 120.0
    assert data["first_price"] == 100.0
    assert data["last_price"] == 140.0
# Test error handling for BusinessComputationError
def test_get_market_chart_stats_computation_error(monkeypatch):
    # Patch compute_market_chart_stats to raise BusinessComputationError
    def _raise_computation_error(symbol, currency, days, provider):
        raise domain_errors.BusinessComputationError("Error computing statistics from market chart data.")
    
    monkeypatch.setattr(api_market_chart,"compute_market_chart_stats",_raise_computation_error)

    # Make the API call
    response = client.get(
        "/market_chart/stats",
        params={
            "symbol": 'bitcoin',
            "currency": 'usd',
            "days": 5,
            "provider": 'coingecko',
        }
    )
    # Check the response
    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Error computing statistics from market chart data."

#test /market_chart/dataframe endpoint
def test_get_market_chart_dataframe_success(monkeypatch):
    """
    Test the enriched dataframe endpoint.
    Ensures that DataFrameResponse is returned correctly (columns + rows).
    """

    # Fake DataFrame returned by compute_enriched_market_chart
    fake_df = pd.DataFrame(
        {
            "timestamp": [
                datetime(2023, 1, 1),
                datetime(2023, 1, 2),
                datetime(2023, 1, 3),
            ],
            "price": [100.0, 110.0, 120.0],
        }
    )

    # Monkeypatch the domain service used by the endpoint
    def fake_enriched(*args, **kwargs):
        return fake_df

    monkeypatch.setattr(
        api_market_chart, "compute_enriched_market_chart", fake_enriched
    )

    # Perform request
    response = client.get(
        "/market_chart/dataframe",
        params={
            "symbol": "bitcoin",
            "currency": "usd",
            "days": 3,
            "provider": "coingecko",
        },
    )

    # Validations
    assert response.status_code == 200
    data = response.json()

    # DataFrameResponse schema
    assert data["columns"] == ["timestamp", "price"]
    assert len(data["rows"]) == 3

    # Check first and last rows
    assert data["rows"][0][1] == 100.0
    assert data["rows"][-1][1] == 120.0

def test_get_market_chart_dataframe_computation_error(monkeypatch):
    """
    If compute_enriched_market_chart raises BusinessComputationError,
    the endpoint must return HTTP 500 with correct detail.
    """
    from app.domain import errors as domain_errors

    def fake_error(*args, **kwargs):
        raise domain_errors.BusinessComputationError("Computation failed")

    monkeypatch.setattr(
        api_market_chart, "compute_enriched_market_chart", fake_error
    )

    response = client.get(
        "/market_chart/dataframe",
        params={
            "symbol": "bitcoin",
            "currency": "usd",
            "days": 5,
            "provider": "coingecko",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Computation failed"