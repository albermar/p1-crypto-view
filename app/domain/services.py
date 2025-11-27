from app.domain.entities import Symbol, Currency, Provider, MarketChartData, PricePoint, ResampleFrequency
from app.infrastructure.coingecko import infra_get_parsed_market_chart_coingecko
from app.infrastructure import errors as errors_infra
from app.domain import errors as errors_domain
import pandas as pd
from app.services.analytics import (
    convert_market_chart_data_to_dataframe,
    calculate_stats,
    compute_returns,
    compute_rolling_window,
    resample_price_series,
    trim_date_range,
    normalize_series,
    compute_volatility,
)
from datetime import datetime

DEFAULT_PROVIDER = Provider.COINGECKO
# Business Logic Layer (Domain Services)
# This layer contains business functions that orchestrate the use of entities and infrastructure functions to fulfill business use cases.


# Use case 1: Fetch historical market data from a provider

def fetch_market_chart(
    symbol: Symbol, 
    currency: Currency, 
    days: int, 
    provider: Provider = DEFAULT_PROVIDER
) -> MarketChartData:
    #This business function will fetch market chart data for a given symbol, currency, and number of days from the specified provider.
    if provider is not Provider.COINGECKO:
            raise errors_domain.BusinessProviderNotCompatible(f'Provider {provider} not supported yet in this use case')    
    if days <= 0:
        raise errors_domain.BusinessValidationError(f'Invalid parameters: days={days} must be positive integer')
    
    try:        
        data = infra_get_parsed_market_chart_coingecko(symbol, currency, days)
    except errors_infra.InfrastructureProviderNotCompatibleError as e:
        raise errors_domain.BusinessProviderNotCompatible(f'Provider {provider} not compatible with symbol {symbol} and/or currency {currency}: {e}')
    
    except errors_infra.InfrastructureExternalApiMalformedResponse as e:
        raise errors_domain.BusinessMalformedDataError(f'Malformed data received from provider {provider}: {e}')
    
    except errors_infra.InfrastructureBadURL as e:        
        raise errors_domain.BusinessProviderGeneralError(f'Bad URL error for provider {provider}: {e}')
    
    except errors_infra.InfrastructureValidationError as e:        
        raise errors_domain.BusinessProviderGeneralError(f'Validation error in provider {provider}: {e}')
    
    except errors_infra.InfrastructureExternalApiError as e:        
        raise errors_domain.BusinessProviderGeneralError( f'External API error from provider {provider}: {e}')
    
    except errors_infra.InfrastructureExternalApiTimeout as e:        
        raise errors_domain.BusinessProviderGeneralError( f'External API timeout from provider {provider}: {e}')
    
    #check if the answer is MarketChartData. This is a safety check, in theory the infrastructure layer should always return the correct type.
    if not isinstance(data, MarketChartData):
        raise errors_domain.BusinessMalformedDataError(f'Invalid data type received from provider {provider}, expected MarketChartData, got {type(data)}')
    
    #now check if it's empty data
    if not len(data.points):
        raise errors_domain.BusinessNoDataError(f'No data available for symbol {symbol}, currency {currency}, days {days} from provider {provider}')
    
    return data

# Use case 2: Compute basic statistics from market chart data using pandas

def compute_market_chart_stats(
    symbol: Symbol, 
    currency: Currency, 
    days: int, 
    provider: Provider = DEFAULT_PROVIDER 
    ) -> dict:   
         
    #Get MarketChartData
    mcd = fetch_market_chart(symbol = symbol, currency=currency, days=days, provider=provider)  #reuse the fetch function to validate and get data    
    #Convert to DataFrame
    df = convert_market_chart_data_to_dataframe(marketchartdata=mcd)    
    try:
        #Compute stats of the DataFrame
        stats = calculate_stats(df = df, stats_key='price')    
    except (ValueError, KeyError) as e:
        raise errors_domain.BusinessComputationError(f'Error computing statistics from market chart data: {e}')
    return stats

# Use case 3: Compute enriched market chart data with optional analytics using pandas

def compute_enriched_market_chart(
    symbol: Symbol,
    currency: Currency,
    days: int,
    provider: Provider,
    frequency: ResampleFrequency | None = None,
    window_size: int | None = None,
    normalize_base: float | None = None,
    volatility_window: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
) -> pd.DataFrame:
    
    # 1) Fetch raw chart
    raw_chart: MarketChartData = fetch_market_chart(symbol, currency, days, provider)
    
    # 2) Domain -> DataFrame
    df = convert_market_chart_data_to_dataframe(raw_chart)
    
    try:    
        # 3) Optional range trim
        df = trim_date_range(df, start, end)
        
        #4) Optional resampling
        if frequency is not None:
            df = resample_price_series(df, 'price', frequency)
        
        # 5) Always compute returns
        compute_returns(df, 'price')
        
        # 6) Optional rolling
        if window_size is not None:
            if window_size <= 0:
                raise ValueError(f'Window size must be greater than 0. Got {window_size}')
            compute_rolling_window(df, window_size, "price")
        
        # 7) Optional volatility
        if volatility_window is not None:
            if volatility_window <= 1:
                raise ValueError(f'Volatility window must be greater than 1. Got {volatility_window}')
            compute_volatility(df, "price", volatility_window)
        
        # 8) Optional normalization
        if normalize_base is not None:
            normalize_series(df, "price", normalize_base)
    
    except (KeyError, ValueError) as e:
        raise errors_domain.BusinessComputationError(f'Error computing enriched market chart with pandas {e}')
    
    return df
