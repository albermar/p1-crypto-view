import random
from app.domain.entities import Symbol, Currency, MarketChartData
import pandas as pd
from datetime import datetime
#Analytics layer services


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
    if df.empty:
        raise ValueError('Cannot compute stats on an empty DataFrame')
    if not stats_key or not isinstance(stats_key, str):
        raise ValueError('numeric_key must be a non-empty string (e.g. "price")')
    if stats_key not in df.columns:
        raise KeyError(f"Column '{stats_key}' not found in DataFrame")
    
    series = df[stats_key]
    
    if series.isna().all():
        raise ValueError(f'All values in the column {stats_key} are NaN, cannot compute statistics.')
    
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
    
    


        
        
        
        
        
    
    



if __name__ == "__main__":    
    #test convert_market_chart_data_to_dataframe witha  marketchart data example:
    from app.domain.entities import PricePoint
     #sample poins is a list[PricePoint] 
    sample_points = [ ]
    for i in range(100):
        p = PricePoint(timestamp=datetime(2024, 1, 1, 0, 0), price = random.random() + i**(1.25))
        sample_points.append(p)
        
    sample_chart = MarketChartData(Symbol.BTC, Currency.USD, sample_points)
    df = convert_market_chart_data_to_dataframe(sample_chart)   
    #compute stats:
    stats = compute_stats(df, 'price')
    for k, v in stats.items():
        print(f"{k}: {v}")