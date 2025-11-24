from typing import Optional
from fastapi import APIRouter, HTTPException
from app.api.schemas import MarketChartResponse, StatsResponse, DataFrameResponse
from app.domain.entities import ResampleFrequency, Symbol, Currency, Provider
from app.domain.services import fetch_market_chart, compute_market_chart_stats, compute_enriched_market_chart
from app.domain import errors
from app.services.analytics import convert_market_chart_data_to_dataframe
from datetime import datetime


router = APIRouter(prefix = '/market_chart', tags = ['market-chart'])

@router.get('/',
            response_model = MarketChartResponse, 
            summary = 'Fetch crypto data for market chart', 
            description='Retrieve historical market chart data for a specified cryptocurrency, currency, and number of days.')
def get_market_chart(symbol: Symbol, currency: Currency, days: int, provider: Provider):   
    
    try:
        #Fetch market chart data from the business layer
        data = fetch_market_chart(symbol, currency, days, provider) #Domain entity MarketChartData        
         
    except errors.BusinessValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))     
    
    except errors.BusinessProviderNotCompatible as e:
        raise HTTPException(status_code=400, detail=str(e))     
    
    except errors.BusinessProviderGeneralError as e:
        raise HTTPException(status_code=500, detail=str(e))     
    
    except errors.BusinessMalformedDataError as e:
        raise HTTPException(status_code=500, detail=str(e))     
    
    except errors.BusinessNoDataError as e:
        raise HTTPException(status_code=404, detail=str(e))     
    
    #return pydantic model response
    return MarketChartResponse.from_domain(data) #Pydantic model

@router.get('/stats', 
            response_model = StatsResponse,
            summary = 'Fetch statistics for market chart data',
            description='Retrieve statistical information (mean, median, std deviation) for historical market chart data of a specified cryptocurrency, currency, and number of days.')
def get_market_chart_stats(symbol: Symbol, currency: Currency, days: int, provider: Provider):
    
    try:
        stats = compute_market_chart_stats(symbol, currency, days, provider)
    except errors.BusinessValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))     
    
    except errors.BusinessProviderNotCompatible as e:
        raise HTTPException(status_code=400, detail=str(e))     
    
    except errors.BusinessProviderGeneralError as e:
        raise HTTPException(status_code=500, detail=str(e))     
    
    except errors.BusinessMalformedDataError as e:
        raise HTTPException(status_code=500, detail=str(e))     
    
    except errors.BusinessNoDataError as e:
        raise HTTPException(status_code=404, detail=str(e))     
    
    except errors.BusinessComputationError as e:
        raise HTTPException(status_code=500, detail=str(e))     
    
    stats = StatsResponse.from_dict(stats)
    
    return stats

@router.get('/dataframe', response_model = DataFrameResponse,
            summary = 'Fetch market chart data as DataFrame',
            description='Retrieve historical market chart data for a specified cryptocurrency, currency, and number of days in a tabular DataFrame format.')
def get_market_chart_dataframe(
    symbol: Symbol, 
    currency: Currency, 
    days: int, 
    provider: Provider, 
    frequency: Optional[ResampleFrequency] = None,
    window_size: Optional[int] = None,
    normalize_base: Optional[float] = None,
    volatility_window: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    ):
    """
    Endpoint returning an enriched DataFrame:
    - timestamp, price
    - pct_change, acum_pct_change
    - rolling mean (if window_size)
    - volatility (if volatility_window)
    - normalized price (if normalize_base)
    - plus weekly fields if resampled to weekly
    """
    try:
        df = compute_enriched_market_chart(
            symbol=symbol,
            currency=currency,
            days=days,
            provider=provider,
            frequency=frequency,
            window_size=window_size,
            normalize_base=normalize_base,
            volatility_window=volatility_window,
            start=start,
            end=end,
        )    
         
    except errors.BusinessValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))     
    
    except errors.BusinessProviderNotCompatible as e:
        raise HTTPException(status_code=400, detail=str(e))     
    
    except errors.BusinessProviderGeneralError as e:
        raise HTTPException(status_code=500, detail=str(e))     
    
    except errors.BusinessMalformedDataError as e:
        raise HTTPException(status_code=500, detail=str(e))     
    
    except errors.BusinessNoDataError as e:
        raise HTTPException(status_code=404, detail=str(e)) 
       
    except errors.BusinessComputationError as e:
        # raised by compute_enriched_market_chart when pandas layer fails
        raise HTTPException(status_code=500, detail=str(e)) 
    
    #Convert Enriched DataFrame to DataFrameResponse
    return DataFrameResponse.from_dataframe(df)


