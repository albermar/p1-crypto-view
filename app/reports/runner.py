# runner.py
# Orquesta script to fetch enriched crypto price data and generate plots using specified parameters.

import argparse
from pathlib import Path

import pandas as pd

from app.domain.entities import Symbol, Currency, Provider, ResampleFrequency
from app.domain.services import compute_enriched_market_chart
from app.reports.plots import plot_enriched_price 


def run_enriched_plot(
    symbol: Symbol,
    currency: Currency,
    days: int,
    provider: Provider,
    out_path: Path,
    window_size: int = 15,
    volatility_window: int = 15,
    normalize_base: float = 100.0,
    resample_frequency: ResampleFrequency | None = ResampleFrequency.WEEKLY,
) -> None:
    """
    Orquesta: fetch -> enriched df -> plot enriched PNG.
    """
    print(f"[runner] Fetching & computing enriched chart for {symbol.name}/{currency.name} ({days} days) from {provider.name}...")

    df: pd.DataFrame = compute_enriched_market_chart(
        symbol=symbol,
        currency=currency,
        days=days,
        provider=provider,
        frequency=None,         # keep raw daily data
        window_size=window_size,
        normalize_base=normalize_base,
        volatility_window=volatility_window,
    )

    print(f"[runner] DataFrame shape: {df.shape}")

    # Ensure output directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[runner] Generating enriched plot -> {out_path} ...")
    plot_enriched_price(
        df=df,
        out_path=str(out_path),
        symbol=symbol,
        currency=currency,
        provider=provider,
        price_key="price",
        resample_frequency=resample_frequency,
    )
    print("[runner] Done ✅")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Runner for enriched crypto price analytics & plots."
    )

    parser.add_argument(
        "--symbol",
        type=str,
        default="BTC",
        help="Crypto symbol (Enum name, e.g. BTC, ETH).",
    )
    parser.add_argument(
        "--currency",
        type=str,
        default="USD",
        help="Fiat currency (Enum name, e.g. USD, EUR).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Number of historical days.",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="COINGECKO",
        help="Provider enum name (currently COINGECKO).",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=15,
        help="Rolling window size for moving average & volatility.",
    )
    parser.add_argument(
        "--normalize-base",
        type=float,
        default=100.0,
        help="Base index for normalized price series.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs/enriched_all_analytics.png",
        help="Path for output PNG.",
    )
    parser.add_argument(
        "--resample-frequency",
        type=str,
        default="WEEKLY",
        choices=[f.name for f in ResampleFrequency],
        help="Resample frequency for overlay (visual only).",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Map strings to enums
    symbol = Symbol[args.symbol.upper()]
    currency = Currency[args.currency.upper()]
    provider = Provider[args.provider.upper()]
    resample_frequency = ResampleFrequency[args.resample_frequency.upper()]

    out_path = Path(args.output)
    #add to the out path file name the symbol, currency, provider. without new folder
    out_path = out_path.with_name(f"{symbol.name}_{currency.name}_{provider.name}_" + out_path.name)
    
    
    

    run_enriched_plot(
        symbol=symbol,
        currency=currency,
        days=args.days,
        provider=provider,
        out_path=out_path,
        window_size=args.window,
        volatility_window=args.window,
        normalize_base=args.normalize_base,
        resample_frequency=resample_frequency,
    )


if __name__ == "__main__":
    main()
