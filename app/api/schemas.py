from datetime import datetime
from typing import Any
from pydantic import BaseModel
from app.domain.entities import Symbol, Currency, MarketChartData, PricePoint
import pandas as pd

class PricePointResponse(BaseModel):
    timestamp: datetime
    price: float
    
    @classmethod
    def from_domain(cls, domain_price_point: PricePoint) -> 'PricePointResponse':
        timestamp = domain_price_point.timestamp
        price = domain_price_point.price 
        
        return cls(timestamp=timestamp, price=price)     

class MarketChartResponse(BaseModel):
    symbol: Symbol
    currency: Currency
    points: list[PricePointResponse]
    
    @classmethod
    def from_domain(cls, domain_market_chart_data: MarketChartData) -> 'MarketChartResponse':
        sym = domain_market_chart_data.symbol
        cur = domain_market_chart_data.currency
        pts = []
        for price_point in domain_market_chart_data.points:
            #Convert to PricePointResponse and append to my list of PricePointResponse
            pts.append(PricePointResponse.from_domain(price_point))
        #WITH LIST COMPREHENSION
        #pts = [PricePointResponse.from_domain(p) for p in domain_market_chart_data.points]
        return cls(symbol=sym, currency=cur, points=pts)

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
    Non-professional way to do it:
    @classmethod
    def from_dict(cls, dict_stats: dict) -> 'StatsResponse':
        count = dict_stats['count']
        min_price = dict_stats['min_price']
        max_price = dict_stats['max_price']
        mean_price = dict_stats['mean_price']
        median_price = dict_stats['median_price']
        std_dev = dict_stats['std_dev']
        variance = dict_stats['variance']
        first_price = dict_stats['first_price']
        last_price = dict_stats['last_price']
        percent_change = dict_stats['percent_change']
        return cls(
            count=count,
            min_price=min_price,
            max_price=max_price,
            mean_price=mean_price,
            median_price=median_price,
            std_dev=std_dev,
            variance=variance,
            first_price=first_price,
            last_price=last_price,
            percent_change=percent_change
        )
        '''

class DataFrameResponse(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> 'DataFrameResponse':
        columns =  list(df.columns)
        rows = df.values.tolist()
        return cls(columns=columns, rows=rows)
     
        
        
        
        