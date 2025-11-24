'''
General philosophy:
    1 ) Happy path 
    2 ) Edge cases / Boundaries (single row, constant price, minimal window, etc)
    3 ) Error behaviout (inputs that should raise ValueError, KeyError, etc)
    4 ) Side effects
        * Does it modify the DataFrame in place? Does it returns a new one?
        * Does it keep the index? Columns? Data types?

Functions to test:
    _validate_numeric_series
    convert_market_chart_data_to_dataframe    
    calculate_stats    
    compute_returns
    compute_rolling_window
    resample_price_series
    trim_date_range
    normalize_series
    compute_volatility

'''
import pytest
from datetime import datetime
import pandas as pd
from app.domain.services import compute_enriched_market_chart
from app.services.analytics import (
    _validate_numeric_series,
    convert_market_chart_data_to_dataframe,
    calculate_stats,
    compute_returns,
    compute_rolling_window,
    resample_price_series,
    trim_date_range,
    normalize_series,
    compute_volatility
)
from app.domain.entities import Symbol, Currency, PricePoint, MarketChartData, ResampleFrequency

# Testing steps (no code):
# 1) Create sample MarketChartData with known PricePoints
# 2) Convert to DataFrame using convert_market_chart_data_to_dataframe
# 3) Test each function with the DataFrame and verify outputs

# Sample MarketChartData for testing
def build_sample_marketchartdata():
    """
    Build a MarketChartData object for manual testing.
    This is NOT a pytest fixture — just a normal function.
    """
    points = [
        PricePoint(timestamp=datetime(2023, 1, 1), price=100.0),
        PricePoint(timestamp=datetime(2023, 1, 2), price=110.0),
        PricePoint(timestamp=datetime(2023, 1, 3), price=105.0),
        PricePoint(timestamp=datetime(2023, 1, 4), price=115.0),
        PricePoint(timestamp=datetime(2023, 1, 5), price=120.0),
    ]
    return MarketChartData(symbol=Symbol.BTC, currency=Currency.USD, points=points)

def build_sample_marketchartdata_2():
    """
    Build a MarketChartData object for manual testing.
    This is NOT a pytest fixture — just a normal function.
    """
    points = [
        PricePoint(timestamp=datetime(2025, 11, 17), price=1.0),
        PricePoint(timestamp=datetime(2025, 11, 18), price=2.0),
        PricePoint(timestamp=datetime(2025, 11, 19), price=3.0),
        PricePoint(timestamp=datetime(2025, 11, 20), price=4.0),
        PricePoint(timestamp=datetime(2025, 11, 21), price=5.0),
        PricePoint(timestamp=datetime(2025, 11, 22), price=6.0),
        PricePoint(timestamp=datetime(2025, 11, 23), price=7.0),
        PricePoint(timestamp=datetime(2025, 11, 24), price=8.0)
    ]
    return MarketChartData(symbol=Symbol.BTC, currency=Currency.USD, points=points)

# Test convert_market_chart_data_to_dataframe
def test_convert_market_chart_data_to_dataframe():
    sample_data = build_sample_marketchartdata()
    df = convert_market_chart_data_to_dataframe(sample_data)
    print(df)
    assert len(df) == 5
    assert list(df.columns) == ['timestamp', 'price']    
    assert df.iloc[0]['timestamp'] == datetime(2023, 1, 1)
    assert df.iloc[0]['price'] == 100.0
    assert df.iloc[4]['timestamp'] == datetime(2023, 1, 5)
    assert df.iloc[4]['price'] == 120.0
    
    #now test edge: MarketChartData with no points
    empty_data = MarketChartData(symbol=Symbol.BTC, currency=Currency.USD, points=[])
    df_empty = convert_market_chart_data_to_dataframe(empty_data)
    assert len(df_empty) == 0
    assert list(df_empty.columns) == ['timestamp', 'price']
    

# Test _validate_numeric_series
def test_validate_numeric_series():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    
    series = _validate_numeric_series(df, 'price')
    assert series.equals(df['price'])
    
    # Test non-numeric column
    df['non_numeric'] = ['a', 'b', 'c', 'd', 'e']
    with pytest.raises(ValueError):
        _validate_numeric_series(df, 'non_numeric')
    
    # Test missing column
    with pytest.raises(KeyError):
        _validate_numeric_series(df, 'missing_column')
        
    #test all NaN column
    df['all_nan'] = [float('nan')] * len(df)
    with pytest.raises(ValueError):
        _validate_numeric_series(df, 'all_nan') 

# Test calculate_stats
def test_calculate_stats():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    stats = calculate_stats(df, 'price')
    
    assert stats['count'] == 5
    assert stats['min_price'] == 100.0
    assert stats['max_price'] == 120.0
    assert stats['mean_price'] == 110.0
    assert stats['median_price'] == 110.0
    assert round(stats['std_dev'], 5) == 7.90569
    assert round(stats['variance'], 5) == 62.5
    assert stats['first_price'] == 100.0
    assert stats['last_price'] == 120.0
    assert round(stats['percent_change'], 5) == 20.0
    
    #error empty dataframe
    empty_df = pd.DataFrame(columns=['timestamp', 'price'])
    with pytest.raises(ValueError):
        calculate_stats(empty_df, 'price')  
    #column doesn't exist
    with pytest.raises(KeyError):
        calculate_stats(df, 'missing_column')
    #edge: all values are the same
    constant_df = pd.DataFrame({'timestamp': [datetime(2023, 1, i) for i in range(1,6)],
                                'price': [50.0] * 5})
    stats_constant = calculate_stats(constant_df, 'price')
    assert stats_constant['std_dev'] == 0.0
    assert stats_constant['variance'] == 0.0

# Test compute_returns
def test_compute_returns():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    compute_returns(df, 'price')
    
    expected_pct_change = [float('nan'), 10.0, -4.54545, 9.52381, 4.34783]
    expected_acum_pct_change = [0.0, 10.0, 5.0, 15.0, 20.0]
    
    for i in range(len(df)):
        if i == 0:
            assert pd.isna(df.iloc[i]['pct_change'])
        else:
            assert round(df.iloc[i]['pct_change'], 5) == round(expected_pct_change[i], 5)
        assert round(df.iloc[i]['acum_pct_change'], 5) == round(expected_acum_pct_change[i], 5)

    #edge: constant series [100, 100, 100]
    constant_df = pd.DataFrame({'timestamp': [datetime(2023, 1, i) for i in range(1,6)],
                                'price': [100.0] * 5})
    compute_returns(constant_df, 'price')
    for i in range(len(constant_df)):
        if i == 0:
            assert pd.isna(constant_df.iloc[i]['pct_change'])
        else:
            assert constant_df.iloc[i]['pct_change'] == 0.0
            assert constant_df.iloc[i]['acum_pct_change'] == 0.0
    #edge: single row DataFrame
    single_row_df = pd.DataFrame({'timestamp': [datetime(2023, 1, 1)],
                                    'price': [150.0]})
    compute_returns(single_row_df, 'price')
    assert pd.isna(single_row_df.iloc[0]['pct_change'])
    assert single_row_df.iloc[0]['acum_pct_change'] == 0.0
    
    #no column
    with pytest.raises(KeyError):
        compute_returns(single_row_df, 'missing_column')
    
#test compute_rolling_window
def test_compute_rolling_window():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    compute_rolling_window(df, 3, 'price')
    
    expected_rolling_mean_3 = [float('nan'), float('nan'), 105.0, 110.0, 113.33333]
    
    for i in range(len(df)):
        if i < 2:
            assert pd.isna(df.iloc[i]['rolling_mean_3'])
        else:
            assert round(df.iloc[i]['rolling_mean_3'], 5) == round(expected_rolling_mean_3[i], 5)
    #edge: window size = 1 (should equal original series)
    df_window_1 = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    compute_rolling_window(df_window_1, 1, 'price')
    for i in range(len(df_window_1)):
        assert df_window_1.iloc[i]['rolling_mean_1'] == df_window_1.iloc[i]['price']
    #error: window size > len(df), should raise ValueError
    with pytest.raises(ValueError):
        compute_rolling_window(df, 10, 'price')
    #error: missing column
    with pytest.raises(KeyError):
        compute_rolling_window(df, 3, 'missing_column_5')  
    #error: window size <= 0
    with pytest.raises(ValueError):
        compute_rolling_window(df, 0, 'price')
    #error: window size < 0
    with pytest.raises(ValueError):
        compute_rolling_window(df, -2, 'price')
        
#test resample_price_series
def test_resample_price_series():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata_2())    
    resampled_df = resample_price_series(df, 'price', ResampleFrequency.WEEKLY)
    assert len(resampled_df) == 2  # Two weeks
    assert resampled_df.iloc[0]['price'] == 7.0  # last of first week (1-4)
    assert resampled_df.iloc[1]['price'] == 8.0  # last of second week (5-8)

    #side effect: original df should remain unchanged
    assert len(df) == 8
    assert df.iloc[0]['price'] == 1.0
    assert df.iloc[7]['price'] == 8.0
    #edge: other frequency (Monthly)
    resampled_df_monthly = resample_price_series(df, 'price', ResampleFrequency.MONTHLY)
    assert len(resampled_df_monthly) == 1  # One month
    assert resampled_df_monthly.iloc[0]['price'] == 8.0  # last of the month
    #edge: check that adds week number columns if weekly
    resampled_df_weekly = resample_price_series(df, 'price', ResampleFrequency.WEEKLY)
    assert 'week_number' in resampled_df_weekly.columns
    
    #error frequency not supported. Keep in mind that ResampleFrequency is an Enum, so we need to create an invalid one for testing. But Enum prevents that. When we try to create freq = ResampleFrequency('invalid'), it raises an error
    with pytest.raises(ValueError):
        freq = ResampleFrequency('invented_frequency_for_testing')    
        resample_price_series(df, 'price', freq)
    # Edge: timestamps as strings keep in mind that the function does this: # Ensure timestamp is proper datetime    df['timestamp'] = pd.to_datetime(df 'timestamp'])
    df_strings = pd.DataFrame({'timestamp': ['2025-11-17', '2025-11-18', '2025-11-19', '2025-11-20'],
                               'price': [1.0, 2.0, 3.0, 4.0]})
    resampled_df_strings = resample_price_series(df_strings, 'price', ResampleFrequency.DAILY)
    assert len(resampled_df_strings) == 4   

#test trim_date_range
def test_trim_date_range():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata_2())    
    start_date = datetime(2025, 11, 19)
    end_date = datetime(2025, 11, 22)
    trimmed_df = trim_date_range(df, start_date, end_date)
    assert len(trimmed_df) == 4
    assert trimmed_df.iloc[0]['timestamp'] == start_date
    assert trimmed_df.iloc[3]['timestamp'] == end_date
    assert trimmed_df.iloc[0]['price'] == 3.0
    assert trimmed_df.iloc[3]['price'] == 6.0

    #edge: only start date
    trimmed_start_df = trim_date_range(df, start_date, None)
    assert len(trimmed_start_df) == 6   
    assert trimmed_start_df.iloc[0]['timestamp'] == start_date
    #edge: only end date
    trimmed_end_df = trim_date_range(df, None, end_date)
    assert len(trimmed_end_df) == 6
    assert trimmed_end_df.iloc[-1]['timestamp'] == end_date
    #edge: no trimming
    trimmed_none_df = trim_date_range(df, None, None)
    assert len(trimmed_none_df) == len(df)
    #edge: start date after end date (should return empty DataFrame)
    trimmed_empty_df = trim_date_range(df, datetime(2025, 11, 25), datetime(2025, 11, 20))
    assert len(trimmed_empty_df) == 0
    #side: original df should remain unchanged
    assert len(df) == 8
    
#test normalize_series
def test_normalize_series():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    normalize_series(df, 'price', base = 200.0)
    
    expected_normalized_prices = [200.0, 220.0, 210.0, 230.0, 240.0]
    
    column_normalized = f'normalized_price_base_{round(float(200.0), 5)}'     
    for i in range(len(df)):
        assert round(df.iloc[i][column_normalized], 5) == round(expected_normalized_prices[i], 5)

    #edge: constant series
    constant_df = pd.DataFrame({'timestamp': [datetime(2023, 1, i) for i in range(1,6)],
                                'price': [50.0] * 5})
    normalize_series(constant_df, 'price', base=100.0)
    column_normalized_const = f'normalized_price_base_{round(float(100.0), 5)}'
    for i in range(len(constant_df)):
        assert round(constant_df.iloc[i][column_normalized_const], 5) == 100.0
    #error: first element is zero
    zero_first_df = pd.DataFrame({'timestamp': [datetime(2023, 1, i) for i in range(1,6)],
                                  'price': [0.0, 10.0, 20.0, 30.0, 40.0]})
    with pytest.raises(ValueError):
        normalize_series(zero_first_df, 'price', base=100.0)
    #edge: window size = 1 (should equal original series)
    single_row_df = pd.DataFrame({'timestamp': [datetime(2023, 1, 1)],
                                    'price': [150.0]})
    normalize_series(single_row_df, 'price', base=100.0)
    column_normalized_single = f'normalized_price_base_{round(float(100.0), 5)}'
    assert round(single_row_df.iloc[0][column_normalized_single], 5) == round(100.0, 5) 
    #edge: window size < 0
    negative_base_df = pd.DataFrame({'timestamp': [datetime(2023, 1, i) for i in range(1,6)],
                                    'price': [10.0, 20.0, 30.0, 40.0, 50.0]})
    normalize_series(negative_base_df, 'price', base=-100.0)
    column_normalized_negative = f'normalized_price_base_{round(float(-100.0), 5)}'
    for i in range(len(negative_base_df)):
        expected_value = (negative_base_df.iloc[i]['price'] / 10.0) * -100.0
        assert round(negative_base_df.iloc[i][column_normalized_negative], 5) == round(expected_value, 5)
    #edge: window size = 0
    zero_base_df = pd.DataFrame({'timestamp': [datetime(2023, 1, i) for i in range(1,6)],
                                    'price': [10.0, 20.0, 30.0, 40.0, 50.0]})
    normalize_series(zero_base_df, 'price', base=0.0)
    column_normalized_zero = f'normalized_price_base_{round(float(0.0), 5)}'
    for i in range(len(zero_base_df)):
        assert round(zero_base_df.iloc[i][column_normalized_zero], 5) == 0.0
    #edge window > len(df)
    short_df = pd.DataFrame({'timestamp': [datetime(2023, 1, i) for i in range(1,4)],
                                    'price': [10.0, 20.0, 30.0]})
    normalize_series(short_df, 'price', base=100.0) 
    column_normalized_short = f'normalized_price_base_{round(float(100.0), 5)}'
    for i in range(len(short_df)):
        expected_value = (short_df.iloc[i]['price'] / 10.0) * 100.0
        assert round(short_df.iloc[i][column_normalized_short], 5) == round(expected_value, 5)
    #column doesn't exist
    with pytest.raises(KeyError):
        normalize_series(df, 'missing_column', base=100.0)        
    
#test compute_volatility
def test_compute_volatility():
    df = convert_market_chart_data_to_dataframe(build_sample_marketchartdata())
    compute_returns(df, 'price')  # Volatility depends on pct_change
    compute_volatility(df, 'price', window_size=2) #Uses aux_pct_changes = series.pct_change() for calculating changes.
    expected_volatility_2 = [float('nan'), float('nan'), 0.10285, 0.09948, 0.03660]
    for i in range(len(df)):
        if i < 2:
            assert pd.isna(df.iloc[i]['volatility_2'])
        else:
            assert round(df.iloc[i]['volatility_2'], 5) == round(expected_volatility_2[i], 5)
    
#test compute_enriched_market_chart 

    



if __name__ == "__main__":
    # Manual test
    sample_data = build_sample_marketchartdata()
    df = convert_market_chart_data_to_dataframe(sample_data)
    stats = calculate_stats(df, 'price')
    #show volatility of build_sample_marketchartdata
    compute_returns(df, 'price')
    compute_volatility(df, 'price', window_size=2)    
    print(df)