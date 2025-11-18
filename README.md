# Crypto Market Data Fetcher (Clean Architecture)

Small backend project to fetch and visualize crypto market data from external providers (starting with CoinGecko), using a clean, layered architecture.

Current focus: **BTC/ETH price history endpoint** with proper separation of concerns and professional error handling.

---

## Folder structure

```
app/
 ├── 1-api/             # FastAPI routes + Pydantic models
 ├── 2-business/        # Use cases (application / business logic)
 ├── 3-domain/          # Domain entities (dataclasses, value objects)
 ├── 4-infrastructure/  # External providers (CoinGecko, etc.)
 └── 5-tests/           # Unit / integration tests

```

---

## Master table (architecture & errors)

High-level contract of each layer: what it does, what it validates and how errors flow.


| Layer | Input | Output | Responsibility | Errors (Own/Input) | Errors (Received) | Errors (own/processes) |
| --- | --- | --- | --- | --- | --- | --- |
| **API** |  |  |  |  |  |  |
| **Business** | - `Provider` (enum)
- `Symbol` (enum)
- `Currency` (enum)
- days: `int` | Domain entity:
    `MarketDataChart` | - Decide what infrastructure to call by provider
- Call infrastructure to obtain raw data
- Converts raw data to clean (Raw to `MarketDataChart` and `PricePoint`)
 | - `BusinessValidationError` (days ≤ 0 or empty params) 
- `BusinessProviderNotCompatible` (symbol/currency not supported) | -  `BusinessProviderGeneralError` (we don’t have data)
        ← ExternalApiTimeout
        ← ExternalApiError  
        ← ExternalApiMalformedResponse  |  |
| **Infrastructure** | - Provider url: `str`
- symbol: `str`
- currency: `str`
- days: `int` | - Raw Dict | - Call external API for raw data |  - `InfrastructureValidationError` (days ≤ 0 or empty params) |  - `InfrastructureExternalApiTimeout` ← httpx.TimeoutException
- `InfrastructureExternalApiError`  ← (httpx.RequestError) or (non 2xx HTTP status)
 | - `InfrastructureExternalApiMalformedResponse` ← (JSON decode error) or (invalid/missing ‘prices’ key) |

## Domain entities

```python
class Symbol(str, Enum):
	  BTC = "bitcoin"     
    ETH = "ethereum"   
    XRP = "ripple"   

class Currency(str, Enum):
    USD = "usd"     
    EUR = "eur"   
    GBP = "gbp" 
    AUD = "aud"
    CHF = "chf"
    JPY = "jpy" 

class Provider(str, Enum):
		COINGECKO: "coingecko"
		
---

class PricePoint:
		timestamp: datetime
		price: float
		
class MarketChartData:
		symbol: Symbol
		currency: Currency
		points: list[PricePoint]
```

## Api Pydantic models

```python
class PrincePointResponse(BaseModel):
		timestamp: datetime
		price: float
		
class MarketChartDataResponse(BaseModel:
		symbol: Symbol
		currency: Currency
		points: list[PrincePointResponse]
		

class MarketChartRequest(BaseModel):
    symbol: Symbol
    currency: Currency
    days: int
```

## General diagram (high-level flow)

---

```python
[ Client ]
    |
    v
[ API layer ]
  - FastAPI endpoints
  - Pydantic request/response models
  - HTTPException mapping
    |
    v
[ Business layer ]
  - Use cases (e.g. get_market_chart)
  - Validate semantic rules
  - Call infrastructure providers
    |
    v
[ Infrastructure layer ]
  - CoinGecko provider (httpx)
  - Network calls + JSON parsing
  - Wrap external errors
    |
    v
[ External API: CoinGecko ]

```