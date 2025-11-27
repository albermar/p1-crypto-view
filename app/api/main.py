from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.market_chart import router as router_market_chart

app = FastAPI(
    title="Crypto Analytics Engine",
    description="API for fetching, analyzing, and visualizing historical cryptocurrency market data.",
    version="1.0.0",
)

app.include_router(router_market_chart, prefix = '/api/v1')

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False, response_class=HTMLResponse)
async def root() -> str:
    return """
    <html>
        <head>
            <title>Crypto Analytics Engine API</title>
            <meta charset="utf-8" />
            <style>
                body {
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    max-width: 900px;
                    margin: 40px auto;
                    padding: 0 16px;
                    line-height: 1.6;
                    background: #0b1120;
                    color: #e5e7eb;
                }
                h1 {
                    font-size: 2rem;
                    margin-bottom: 0.25rem;
                }
                h2 {
                    margin-top: 2rem;
                    margin-bottom: 0.5rem;
                    font-size: 1.2rem;
                    color: #bfdbfe;
                }
                p {
                    margin: 0.25rem 0 0.75rem 0;
                }
                a {
                    color: #60a5fa;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                .tag {
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 999px;
                    background: #111827;
                    border: 1px solid #1f2937;
                    font-size: 0.75rem;
                    margin-right: 4px;
                    color: #9ca3af;
                }
                code {
                    background: #020617;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-size: 0.85rem;
                    border: 1px solid #111827;
                }
                ul {
                    padding-left: 1.25rem;
                    margin-top: 0.25rem;
                    margin-bottom: 0.75rem;
                }
                li {
                    margin-bottom: 0.3rem;
                }
                .section {
                    padding: 16px 14px;
                    border-radius: 12px;
                    border: 1px solid #1f2937;
                    background: radial-gradient(circle at top left, #111827, #020617);
                    margin-top: 1rem;
                }
                .small {
                    font-size: 0.8rem;
                    color: #9ca3af;
                }
                hr {
                    border: none;
                    border-top: 1px solid #1f2937;
                    margin: 2rem 0 1.5rem 0;
                }
            </style>
        </head>
        <body>
            <h1>Crypto Analytics Engine API</h1>
            <p>
                Backend for fetching, analyzing, and visualizing historical crypto market data
                using FastAPI and pandas.
            </p>

            <img src="/static/example_deploy.png" 
            alt="Example enriched plot" 
            style="display:block; margin:20px auto; max-width:70%; border-radius:12px;">
            
            <div class="section">
                <h2>📚 Documentation</h2>
                <ul>
                    <li>
                        <strong><a href="/docs">/docs</a></strong> — Interactive Swagger documentation.
                        Test all endpoints directly in the browser.
                    </li>
                    <li>
                        <strong><a href="/openapi.json">/openapi.json</a></strong> — Raw OpenAPI schema
                        (JSON) for integration with external tools.
                    </li>
                </ul>
            </div>

            <div class="section">
                <h2>🔌 Core Data Endpoints (JSON)</h2>
                <p>All endpoints are served under <code>/api/v1/market_chart</code>.</p>
                <ul>
                    <li>
                        <strong>Raw market data</strong><br />
                        <a href="/api/v1/market_chart/?symbol=bitcoin&currency=eur&days=30&provider=coingecko">
                            /api/v1/market_chart/?symbol=bitcoin&amp;currency=eur&amp;days=30&amp;provider=coingecko
                        </a><br />
                        <span class="small">
                            Returns the historical price series for a crypto pair and provider.
                        </span>
                    </li>
                    <li>
                        <strong>Summary statistics</strong><br />
                        <a href="/api/v1/market_chart/stats?symbol=bitcoin&currency=eur&days=30&provider=coingecko">
                            /api/v1/market_chart/stats?symbol=bitcoin&amp;currency=eur&amp;days=30&amp;provider=coingecko
                        </a><br />
                        <span class="small">
                            Returns count, min, max, mean, median, standard deviation, variance, first/last price and percent change.
                        </span>
                    </li>
                    <li>
                        <strong>Enriched DataFrame (analytics)</strong><br />
                        <a href="/api/v1/market_chart/dataframe?symbol=ethereum&currency=usd&days=60&provider=coingecko&window_size=10&volatility_window=20&normalize_base=100&frequency=weekly">
                            /api/v1/market_chart/dataframe?symbol=ethereum&amp;currency=usd&amp;days=60&amp;provider=coingecko&amp;window_size=10&amp;volatility_window=20&amp;normalize_base=100&amp;frequency=weekly
                        </a><br />
                        <span class="small">
                            Returns an enriched pandas DataFrame (encoded as JSON) with returns, rolling windows,
                            volatility, normalization and optional resampling (daily, weekly, monthly, yearly).
                        </span>
                    </li>
                </ul>
            </div>

            <div class="section">
                <h2>📈 Enriched Plot Endpoint (PNG)</h2>
                <p>
                    The backend can also generate PNG plots with multiple analytics overlays
                    (price, rolling mean, volatility, normalization, optional resampling).
                </p>
                <ul>
                    <li>
                        <strong>Enriched plot (BTC / EUR — last 60 days)</strong><br />
                        <a href="/api/v1/market_chart/bitcoin/eur/plot-enriched?days=60&provider=coingecko&window_size=10&volatility_window=5&normalize_base=100">
                            /api/v1/market_chart/bitcoin/eur/plot-enriched?days=60&amp;provider=coingecko&amp;window_size=10&amp;volatility_window=5&amp;normalize_base=100
                        </a><br />
                        <span class="small">
                            Returns a binary PNG image suitable for dashboards or external apps.
                        </span>
                    </li>
                </ul>
            </div>

            <div class="section">
                <h2>🧪 Ready-to-use parameter examples</h2>
                <p>
                    Symbols: <code>bitcoin</code>, <code>ethereum</code>, <code>ripple</code><br />
                    Currencies: <code>usd</code>, <code>eur</code>, <code>gbp</code>, <code>chf</code>, <code>jpy</code><br />
                    Provider: <code>coingecko</code><br />
                    Frequency (resampling): <code>daily</code>, <code>weekly</code>, <code>monthly</code>, <code>yearly</code>
                </p>
                <p class="small">
                    You can plug these values into any of the endpoints above or experiment with them in <a href="/docs">/docs</a>.
                </p>
            </div>

            <div class="section">
                <h2>💻 Source Code & Tech Stack</h2>
                <p>
                    GitHub Repository:
                    <a href="https://github.com/albermar/crypto-analytics-engine.git" target="_blank" rel="noreferrer">
                        github.com/albermar/crypto-analytics-engine
                    </a>
                </p>
                <p>
                    <span class="tag">FastAPI</span>
                    <span class="tag">Python 3.11</span>
                    <span class="tag">pandas</span>
                    <span class="tag">Matplotlib</span>
                    <span class="tag">httpx</span>
                    <span class="tag">CoinGecko</span>
                    <span class="tag">Render</span>
                </p>
            </div>

            <hr />

            <p class="small">How to use this API:</p>
            <ul class="small">
                <li>Review endpoint parameters and schemas in <code>/docs</code>.</li>
                <li>Call the endpoints from your code using any HTTP client (Python, JS, etc.).</li>
                <li>Use the outputs for quantitative analysis, dashboards, or trading experiments.</li>
                <li>
                    Note: This service relies on public providers (e.g. CoinGecko) under free plans.
                    You may encounter HTTP 429 rate limits if too many requests are made.
                </li>
            </ul>
        </body>
    </html>
    """