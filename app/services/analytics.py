import random
from app.domain.entities import Symbol, Currency, MarketChartData
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

def compute_stats(df: pd.DataFrame, stats_key: str) -> dict:
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

# compute_returns
# compute_rolling_window
# resample_price_series
def compute_returns (df: pd.DataFrame) -> pd.DataFrame:
    '''
    This function will add 2 columns to the price series, with same length
    pct_change: % of change respect the PREVIOUS point (i-(i-1))/(i-1) * 100
    acum_pct_change: % of change respect the FIRST point (i-(0))/(0) * 100
    '''
    series = _validate_numeric_series(df, 'price')    

    #here we have the series with prices.
    #content example of series:
    #how do we access prices? 
    # df['price']
    # df.price
    # timestamp
    # 2024-01-01 00:00:00    30000.0
    # 2024-01-01 01:00:00    30100

    df = df.copy()  # to avoid modifying the original DataFrame
    #compute the pct change manually:
    pct_change_label = pcl = 'pct_change'
    for i in range(len(df)):
        if i == 0:
            df.at[i]
        else:
            df.at[i, pcl] =


    


    return series

if __name__ == "__main__":
    #test convert_market_chart_data_to_dataframe witha  marketchart data example:
    from app.domain.entities import PricePoint
     #sample poins is a list[PricePoint] 
    sample_points = [ ]
    for i in range(20):
        p = PricePoint(timestamp=datetime(2024, 1, 1, 0, 0), price = random.random() + i**(1.25))
        sample_points.append(p)
        
    sample_chart = MarketChartData(Symbol.BTC, Currency.USD, sample_points)
    df = convert_market_chart_data_to_dataframe(sample_chart)   
    #compute stats:
    
    stats = compute_stats(df, 'price')
    #for k, v in stats.items():
     #   print(f"{k}: {v}")
    
    #print df dataframe:
    #print(df)

    df_with_returns = compute_returns(df)
    print(df_with_returns.head(10))
    