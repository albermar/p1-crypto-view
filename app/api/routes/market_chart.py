from fastapi import APIRouter, HTTPException
from app.api.schemas import MarketChartResponse, StatsResponse
from app.domain.entities import Symbol, Currency, Provider
from app.domain.services import fetch_market_chart, compute_market_chart_stats
from app.domain import errors


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




