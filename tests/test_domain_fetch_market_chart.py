import pytest
from datetime import datetime

from app.domain.entities import Symbol, Currency, Provider, MarketChartData, PricePoint
from app.domain.services import fetch_market_chart
from app.domain import errors as errors_domain
from app.infrastructure import errors as errors_infra

'''
Tests:
1. days <= 0 raises BusinessValidationError
2. Provider not supported raises BusinessProviderNotCompatible
3. No data returned raises BusinessNoDataError
4. Malformed data from infrastructure raises BusinessMalformedDataError
5. Infrastructure errors are mapped to BusinessProviderGeneralError
6. Successful data fetch returns MarketChartData with correct attributes
'''

def test_fetch_market_chart_invalid_days():
    with pytest.raises(errors_domain.BusinessValidationError):
        fetch_market_chart(Symbol.BTC, Currency.USD, 0, Provider.COINGECKO)

def test_fetch_market_chart_unsupported_provider():
    with pytest.raises(errors_domain.BusinessProviderNotCompatible):
        fetch_market_chart(Symbol.BTC, Currency.USD, 10, Provider.__UNSUPPORTED__)
        
def test_fetch_market_chart_no_data(monkeypatch):
    def mock_infra_get_parsed_market_chart_coingecko(sym, curr, days):
        return MarketChartData(sym, curr, [])
    
    monkeypatch.setattr(
        'app.domain.services.infra_get_parsed_market_chart_coingecko', 
        mock_infra_get_parsed_market_chart_coingecko
    )
    
    with pytest.raises(errors_domain.BusinessNoDataError):
        fetch_market_chart(Symbol.BTC, Currency.USD, 10, Provider.COINGECKO)

def test_fetch_market_chart_malformed_data(monkeypatch):    
    def mock_infra_get_parsed_market_chart_coingecko(sym, curr, days):
        raise errors_infra.InfrastructureExternalApiMalformedResponse('Malformed response')
    
    monkeypatch.setattr(
        'app.domain.services.infra_get_parsed_market_chart_coingecko', 
        mock_infra_get_parsed_market_chart_coingecko
    )
    
    with pytest.raises(errors_domain.BusinessMalformedDataError):
        fetch_market_chart(Symbol.BTC, Currency.USD, 10, Provider.COINGECKO)

def test_fetch_market_chart_infrastructure_errors(monkeypatch):    
    infra_errors = [
        errors_infra.InfrastructureBadURL('Bad URL'),
        errors_infra.InfrastructureValidationError('Validation error'),
        errors_infra.InfrastructureExternalApiError('API error'),
        errors_infra.InfrastructureExternalApiTimeout('Timeout error')
    ]
    
    for infra_error in infra_errors:
        def mock_infra_get_parsed_market_chart_coingecko(sym, curr, days):
            raise infra_error
        
        monkeypatch.setattr(
            'app.domain.services.infra_get_parsed_market_chart_coingecko', 
            mock_infra_get_parsed_market_chart_coingecko
        )
        
        with pytest.raises(errors_domain.BusinessProviderGeneralError):
            fetch_market_chart(Symbol.BTC, Currency.USD, 10, Provider.COINGECKO)

def test_fetch_market_chart_success(monkeypatch):   
    def mock_infra_get_parsed_market_chart_coingecko(sym, curr, days):
        points = [
            PricePoint(datetime(2023, 1, 1, 0, 0), 30000.0),
            PricePoint(datetime(2023, 1, 2, 0, 0), 31000.0),
            PricePoint(datetime(2023, 1, 3, 0, 0), 32000.0)
        ]
        return MarketChartData(sym, curr, points)
    
    monkeypatch.setattr(
        'app.domain.services.infra_get_parsed_market_chart_coingecko', 
        mock_infra_get_parsed_market_chart_coingecko
    )
    
    data = fetch_market_chart(Symbol.BTC, Currency.USD, 10, Provider.COINGECKO)
    
    assert isinstance(data, MarketChartData)
    assert data.symbol == Symbol.BTC
    assert data.currency == Currency.USD
    assert len(data.points) == 3
    assert data.points[0].price == 30000.0
    assert data.points[1].timestamp == datetime(2023, 1, 2, 0, 0)
    assert data.points[2].price == 32000.0
           