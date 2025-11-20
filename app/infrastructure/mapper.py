from app.domain.entities import Symbol, Currency, Provider
from typing import Dict
from app.infrastructure.errors import InfrastructureProviderNotCompatibleError

# -------- Mappers -------- #
SymbolMap   = Dict[Symbol, str]
CurrencyMap = Dict[Currency, str]

MAPPER_SYMBOL_PROVIDER: Dict[Provider, SymbolMap] = {
    Provider.COINGECKO : {
        Symbol.BTC : "bitcoin",     
        Symbol.XRP : "ripple",
        Symbol.ETH : "ethereum"
        }, 
    Provider.BINANCE : {
        Symbol.BTC : "??",     
        Symbol.XRP : "??",
        Symbol.ETH : "??"
        }
 }

MAPPER_CURRENCY_PROVIDER: Dict[Provider, CurrencyMap] = {
    Provider.COINGECKO : {
        Currency.USD : "usd",
        Currency.EUR : "eur",
        Currency.GBP : "gbp",
        Currency.AUD : "aud",
        Currency.CHF : "chf",
        Currency.JPY : "jpy"
        }, 
    Provider.BINANCE : {
        Currency.USD : "???",
        Currency.EUR : "???",
        Currency.GBP : "???",
        Currency.AUD : "???",
        Currency.CHF : "???",
        Currency.JPY : "???"
        }
    }


def map_provider_symbol_id(sym: Symbol, prov: Provider) -> str:    
    try:
        id_sym = MAPPER_SYMBOL_PROVIDER[prov][sym]
        return id_sym
    except KeyError:
        raise InfrastructureProviderNotCompatibleError(f'Symbol: {sym} not supported by Provider: {prov}')

def map_provider_currency_id(cur: Currency, prov: Provider) -> str:    
    try:
        id_cur = MAPPER_CURRENCY_PROVIDER[prov][cur]
        return id_cur
    except KeyError:
        raise InfrastructureProviderNotCompatibleError(f'Currency: {cur} not supported by Provider: {prov}')
    
