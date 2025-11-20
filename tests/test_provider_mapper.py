
# To run the tests, use the command: pytest tests/test_provider_mapper.py

from app.infrastructure.errors import InfrastructureProviderNotCompatibleError 
from app.domain.entities import Symbol, Currency, Provider
from app.infrastructure.mapper import map_provider_symbol_id, map_provider_currency_id
import pytest

#Symbol Tests

TEST_SYMBOL_ID_OK = [
    (Symbol.BTC, Provider.COINGECKO, 'bitcoin'),
    (Symbol.ETH, Provider.COINGECKO, 'ethereum'),
    (Symbol.XRP, Provider.COINGECKO, 'ripple')
]

TEST_SYMBOL_SUPPORTED  = [
    (Symbol.BTC, Provider.COINGECKO),
    (Symbol.ETH, Provider.COINGECKO),
    (Symbol.XRP, Provider.COINGECKO)
]

TEST_UNMAPPEDSYMBOL_ERROR = [
    (Provider.COINGECKO, InfrastructureProviderNotCompatibleError),
]

#Currency Tests

TEST_CURRENCY_ID_OK  = [
    (Currency.EUR, Provider.COINGECKO, 'eur'), 
    (Currency.USD, Provider.COINGECKO, 'usd'),
    (Currency.GBP, Provider.COINGECKO, 'gbp'),
    (Currency.AUD, Provider.COINGECKO, 'aud'),
    (Currency.CHF, Provider.COINGECKO, 'chf'),
    (Currency.JPY, Provider.COINGECKO, 'jpy')
]
TEST_CURRENCY_SUPPORTED  = [
    (Currency.EUR, Provider.COINGECKO), 
    (Currency.USD, Provider.COINGECKO),
    (Currency.GBP, Provider.COINGECKO),
    (Currency.AUD, Provider.COINGECKO),
    (Currency.CHF, Provider.COINGECKO),
    (Currency.JPY, Provider.COINGECKO)
]

TEST_UNMAPPEDCURRENCY_ERROR = [
    (Provider.COINGECKO, InfrastructureProviderNotCompatibleError)
]

def test_symbol_id_ok():
    for sym, prov, expected_id in TEST_SYMBOL_ID_OK:
        assert map_provider_symbol_id(sym, prov) == expected_id

def test_symbol_types_ok():
    for sym, prov in TEST_SYMBOL_SUPPORTED:
        assert isinstance(map_provider_symbol_id(sym, prov), str)
        
def test_unmapped_symbol_error():
    for prov, exc in TEST_UNMAPPEDSYMBOL_ERROR:
        with pytest.raises(exc):
            map_provider_symbol_id(Symbol.__UNMAPPED__, prov)

def test_currency_id_ok():
    for curr, prov, expected_id in TEST_CURRENCY_ID_OK :
        assert map_provider_currency_id(curr, prov) == expected_id

def test_currency_type_string_ok():
    for curr, prov in TEST_CURRENCY_SUPPORTED :
        assert isinstance(map_provider_currency_id(curr, prov), str)

def test_unmappedcurrency_error():
    for prov, exc in TEST_UNMAPPEDCURRENCY_ERROR:
        with pytest.raises(exc):
            map_provider_currency_id(Currency.__UNMAPPED__, prov)

