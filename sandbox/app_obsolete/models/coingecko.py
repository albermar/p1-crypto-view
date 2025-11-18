# pydantic models for coingecko API responses. This means no communication with the API happens here, only data modeling. 

from enum import Enum 
from datetime import datetime
from pydantic import BaseModel

#1 Enum for supported symbols:

class Symbol(str, Enum):    
    BTC = "bitcoin"     
    ETH = "ethereum"   
    XRP = "ripple"    

#what is Enum parameter? 
#2 Enum for supported currencies:
class Currency(str, Enum):    
    USD = "usd"     
    EUR = "eur"   
    GBP = "gbp" 
    AUD = "aud"
    CHF = "chf"
    JPY = "jpy" 
    
    