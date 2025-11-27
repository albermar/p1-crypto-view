import pandas as pd
import pytest
from datetime import datetime, timedelta

from app.domain.entities import (
    Symbol,
    Currency,
    Provider,
    PricePoint,
    MarketChartData,
    ResampleFrequency,
)
from app.domain import services as domain_services
from app.services.analytics import convert_market_chart_data_to_dataframe

# --- Helpers -----------------------------------------------------------------

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


def _fake_fetch_market_chart(symbol, currency, days, provider) -> MarketChartData:
    # Ignore parameters and just return deterministic data
    return _build_fake_marketchartdata(days=days)


# --- Tests -------------------------------------------------------------------


def test_compute_enriched_market_chart_basic(monkeypatch):
    """
    Happy path: no extra options, just ensure we get a DataFrame with timestamp + price.
    """

    # Import here to avoid circulars
    from app.domain.services import compute_enriched_market_chart

    # Patch fetch_market_chart so we don't hit the real infrastructure / HTTP
    monkeypatch.setattr(domain_services, "fetch_market_chart", _fake_fetch_market_chart)

    df = compute_enriched_market_chart(
        symbol=Symbol.BTC,
        currency=Currency.USD,
        days=5,
        provider=Provider.COINGECKO,
        frequency=None,
        window_size=None,
        volatility_window=None,
        normalize_base=None,
        start=None,
        end=None,
    )

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["timestamp", "price", "pct_change", "acum_pct_change"]
    assert len(df) == 5
    assert df["timestamp"].iloc[0] == datetime(2023, 1, 1)
    assert df["price"].iloc[0] == 100.0
    assert df["timestamp"].iloc[-1] == datetime(2023, 1, 5)
    assert df["price"].iloc[-1] == 140.0
    


def test_compute_enriched_market_chart_with_all_features(monkeypatch):
    """
    Use resampling + returns + rolling mean + volatility + normalization + trimming.
    Just check that:
      - We got all expected columns
      - The date range was trimmed
    """

    from app.domain.services import compute_enriched_market_chart

    monkeypatch.setattr(domain_services, "fetch_market_chart", _fake_fetch_market_chart)

    start = datetime(2023, 1, 3)
    end = datetime(2023, 1, 7)

    df = compute_enriched_market_chart(
        symbol=Symbol.BTC,
        currency=Currency.USD,
        days=10,
        provider=Provider.COINGECKO,
        frequency=ResampleFrequency.DAILY,  # 👈 antes WEEKLY
        window_size=3,
        volatility_window=2,
        normalize_base=100.0,
        start=start,
        end=end,
        )
    
    
    # Basic type and non-empty 
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    
    # Check required columns exist (depending on your implementation names)
    expected_columns = {
        "timestamp",
        "price",
        "pct_change",
        "acum_pct_change",
        "rolling_mean_3",
        "volatility_2",
        "normalized_price_base_100.0",
    }

    assert expected_columns.issubset(set(df.columns))

    # Check trimming worked
    assert df["timestamp"].min() >= start
    assert df["timestamp"].max() <= end
    
    #now check resampling with another set and weekly frequency
    raw_df = convert_market_chart_data_to_dataframe(_fake_fetch_market_chart(Symbol.BTC, Currency.USD, 23, Provider.COINGECKO)) 
    df_weekly = compute_enriched_market_chart(
        symbol=Symbol.BTC,
        currency=Currency.USD,
        days=23,
        provider=Provider.COINGECKO,
        frequency=ResampleFrequency.WEEKLY,  
        window_size=3,
        volatility_window=2,
        normalize_base=100.0,
        start=None,
        end=None,
        )
    assert 'week_number' in df_weekly.columns
    #Check that the number of rows is less than original (because of resampling)    
    assert len(df_weekly) < len(raw_df)
    


def test_compute_enriched_market_chart_invalid_params_propagate(monkeypatch):
    """
    If the underlying function raises a BusinessValidationError (for example),
    we expect that to bubble up (or be mapped) and not silently succeed.
    """

    from app.domain import errors as domain_errors
    from app.domain.services import compute_enriched_market_chart

    def fake_fetch_invalid(symbol, currency, days, provider):
        raise domain_errors.BusinessValidationError("Invalid combination")

    monkeypatch.setattr(domain_services, "fetch_market_chart", fake_fetch_invalid)

    with pytest.raises(domain_errors.BusinessValidationError):
        compute_enriched_market_chart(
            symbol=Symbol.BTC,
            currency=Currency.USD,
            days=0,  # invalid days, for instance
            provider=Provider.COINGECKO,
            frequency=None,
            window_size=None,
            volatility_window=None,
            normalize_base=None,
            start=None,
            end=None,
        )
# --- END OF FILE ------------------------------------------------------------


