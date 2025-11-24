from cmath import pi, sin

import random
from app.domain.entities import Symbol, Currency, MarketChartData, PricePoint, PANDAS_RESAMPLING_RULES, ResampleFrequency
import pandas as pd
from datetime import datetime
#Analytics layer services

def _validate_numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    if df.empty:
        raise ValueError('Cannot compute stats on an empty DataFrame')
    if not column or not isinstance(column, str):
        raise ValueError('numeric_key must be a non-empty string (e.g. "price")')
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame")
    
    series = df[column]

    if series.isna().all():
        raise ValueError(f'All values in the column {column} are NaN, cannot compute statistics.')

    return series

def convert_market_chart_data_to_dataframe(marketchartdata: MarketChartData) -> pd.DataFrame:
    data = {
        'timestamp'  : [p.timestamp for p in marketchartdata.points],
        'price'     : [p.price for p in marketchartdata.points]
    }
    return pd.DataFrame(data)


#pandas operations block:
def calculate_stats(df: pd.DataFrame, stats_key: str) -> dict:
    """
    Compute basic statistics for a numeric column in a price DataFrame.
    """
    series = _validate_numeric_series(df, stats_key)
    
    result_dic = {
        "count": int(series.count()),
        "min_price": float(series.min()),
        "max_price": float(series.max()),
        "mean_price": float(series.mean()),
        "median_price": float(series.median()),
        "std_dev": float(series.std()),
        "variance": float(series.var()),
        "first_price": float(series.iloc[0]),
        "last_price": float(series.iloc[-1]),
        "percent_change": float((series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100),
    }
    
    return result_dic

def compute_returns (df: pd.DataFrame, stats_key: str) -> None:
    series = _validate_numeric_series(df, stats_key)
    df['pct_change'] = series.pct_change() * 100    
    df['acum_pct_change'] = (series - series.iloc[0]) / series.iloc[0] * 100   
    #no return, it adds columns to the df

def compute_rolling_window(df: pd.DataFrame, window_size: int, stats_key: str) -> None:
    series = _validate_numeric_series(df, stats_key)
    df[f'rolling_mean_{window_size}'] = series.rolling(window=window_size).mean()
    #no return, it adds column to the df

def resample_price_series(df: pd.DataFrame, price_key: str, frequency: ResampleFrequency) -> pd.DataFrame:
    # Ensure timestamp is proper datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Validate the column exists and is numeric
    _validate_numeric_series(df, price_key)
    
    # Map frequency -> pandas rule
    if frequency not in PANDAS_RESAMPLING_RULES:
        raise ValueError(f"Unsupported resampling frequency: {frequency}")    
    rule = PANDAS_RESAMPLING_RULES[frequency]
        
    # Set timestamp as index
    df_resampled = df.set_index('timestamp')
    
    # Resample using only the price_key column
    df_resampled = df_resampled.resample(rule).agg({price_key: 'last'})
    
    # Forward fill missing values
    df_resampled[price_key] = df_resampled[price_key].ffill()

    # Restore timestamp as a column
    df_resampled = df_resampled.reset_index()
    
    if frequency == ResampleFrequency.WEEKLY:
        #Add a column with the number of the week in the year
        df_resampled['week_number'] = df_resampled['timestamp'].dt.isocalendar().week
        
    
    return df_resampled

def trim_date_range(df: pd.DataFrame, start: datetime | None, end: datetime | None) -> pd.DataFrame:
    df = df.copy()
    if start is not None:
        df = df[df['timestamp'] >= start]
    if end is not None:
        df = df[df['timestamp'] <= end]
    return df

def normalize_series(df: pd.DataFrame, price_key: str, base: float = 100.0) -> None:
    series = _validate_numeric_series(df, price_key)
    first = series.iloc[0]
    if first == 0:
        raise ValueError(f'Cannot normalize series of {price_key} if first element is Zero')
    df[f'normalized_{price_key}_base_{base}'] = (series / first) * base
    #no return, modifies df in place

def compute_volatility(df: pd.DataFrame, price_key: str, window_size: int) -> None:
    series = _validate_numeric_series(df, price_key)
    # Keep in mind that volatility is the standard deviation of a rolling window of percent_changes. That's it.    
    # Step 1: Compute pct_change
    aux_pct_changes = series.pct_change()
    
    #Construict the column name:
    vol_col_name = f'volatility_{window_size}'
    
    # Step 2: Compute the rolling window (of window_size elements) of the pct_change
    
    df[vol_col_name] = aux_pct_changes.rolling(window=window_size).std()
    
    # No return, modifies df in place
    







if __name__ == "__main__":
    sample_points = [ ]
    for i in range(50):
        #ensure datetimes are increasing 1 day from each other
        p = PricePoint(timestamp=datetime(2025, 1, 1, 0, 0) + pd.Timedelta(days=i), price = 4567+10*sin(pi*i/2).real +3*i)
        sample_points.append(p)
    #Convert list of PricePoint to MarketChartData
    sample_chart = MarketChartData(Symbol.BTC, Currency.USD, sample_points)
    #Convert MarketChartData to DataFrame
    df = convert_market_chart_data_to_dataframe(sample_chart)
    #resample:
    df_resampled = resample_price_series(df, 'price', ResampleFrequency.WEEKLY)
    print('Original DataFrame:')
    print (df)
    print('Resampled DataFrame (Weekly):')
    print (df_resampled)
    
    #Now let's test compute_volatility normalize_series trim_date_range
    print('Testing analytics functions:')
    df_trimmed = trim_date_range (df, datetime(2025, 3, 1), datetime(2025, 4, 11))
    print('Trimmed DataFrame (March to June 2025):')
    print(df_trimmed)
    normalize_series(df, 'price', base=100.0)
    print('Normalized price series (base 100):')
    print(df)
    compute_volatility(df, 'price', window_size=3)
    print('DataFrame with 7-day volatility:')
    print(df)
    print(df['volatility_3'] / df.at[3, 'volatility_3'])
    
