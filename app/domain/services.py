from app.domain.entities import Symbol, Currency, Provider, MarketChartData
from app.infrastructure.coingecko import infra_get_parsed_market_chart_coingecko
from app.infrastructure import errors as errors_infra
from app.domain import errors as errors_domain
from app.services.analytics import convert_market_chart_data_to_dataframe, compute_stats

DEFAULT_PROVIDER = Provider.COINGECKO
#Business layer services
# 1 ) Validate business rules
# 2 ) Decides which infrastructure functions to call to fulfill the business use case
# 3 ) Map infrastructure errors to business errors if needed
# 4 ) Return business entities (MarketChartData, PricePoint, etc)

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
        stats = compute_stats(df = df, stats_key='price')    
    except (ValueError, KeyError) as e:
        raise errors_domain.BusinessComputationError(f'Error computing statistics from market chart data: {e}')
    return stats


if __name__ == "__main__":    
    #Simple test of the service function
    try:
        chart = fetch_market_chart(Symbol.BTC, Currency.USD, 20, Provider.COINGECKO)
        print(f'Fetched {len(chart.points)} data points for {chart.symbol} in {chart.currency}')
        for point in chart.points[-5:]:  # Print first 5 points
            print(f'Time: {point.timestamp}, Price: {point.price}')
    except Exception as e:
         print(f'Error: {e}')  