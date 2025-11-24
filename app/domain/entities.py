'''
Symbol
Currency
Provider
PricePoint
MarketDataChart
'''

from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class Symbol(Enum):
    BTC = 'bitcoin'
    XRP = 'ripple'
    ETH = "ethereum"
    __UNMAPPED__ = "__unmapped__"
    

class Currency(Enum):
    USD = "usd"     
    EUR = "eur"   
    GBP = "gbp" 
    AUD = "aud"
    CHF = "chf"
    JPY = "jpy" 
    __UNMAPPED__ = "__unmapped__"

class Provider(Enum):
    COINGECKO   = 'coingecko'
    BINANCE     = 'binance'
    KRAKEN      = 'kraken'
    __UNSUPPORTED__ = '__unsupported__'

#---

#The following 2 classes are immutable (no more attributes) and will be used just for storing data in timestamp, price and symbol, currency and points. 
#@dataclass would make the code with less boilerplate (no __init__ and no __repr__). In this case I will define one class with decorator @dataclass and the other raw mode, in order to learn.

@dataclass(frozen=True)
class PricePoint:
    timestamp: datetime
    price: float


class MarketChartData:
    symbol: Symbol
    currency: Currency
    points: list[PricePoint]
    
    def __init__(self, symbol: Symbol, currency: Currency, points: list[PricePoint]):
        self.symbol = symbol
        self.currency = currency
        self.points = points #Reference assignment, no copy of the list, keep in mind.
        

class ResampleFrequency(Enum):
    DAILY       = 'daily'
    WEEKLY      = 'weekly'
    MONTHLY     = 'monthly'
    YEARLY      = 'yearly'
    
    
    
PANDAS_RESAMPLING_RULES = {
    ResampleFrequency.DAILY: 'D',
    ResampleFrequency.WEEKLY: 'W-SUN',  # Week ends on Sunday
    ResampleFrequency.MONTHLY: 'ME', # Month End. 
    ResampleFrequency.YEARLY: 'Y'
}