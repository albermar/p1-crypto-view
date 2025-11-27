import pandas as pd
import matplotlib.pyplot as plt
from app.domain.entities import Symbol, Currency, Provider, ResampleFrequency
from app.domain.services import compute_enriched_market_chart
from app.services.analytics import (
    resample_price_series,
    calculate_stats,
)

#Use matplotlib and potly

#Not used in the endpoint, but kept for reference
def plot_price(df: pd.DataFrame, out_path: str) -> None:
    
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    #plot
    plt.figure(figsize=(12,6))
    plt.plot(df['timestamp'], df['price'], label='Price', color='blue', linewidth=2)
    plt.xlabel('Timestamp')
    plt.ylabel('Price')
    plt.title('Price Series Over Time')
    plt.grid(True)
    
    # Save in png
    plt.savefig(out_path, format='png', dpi = 300, bbox_inches='tight')
    plt.close()

#Not used in the endpoint, but kept for reference
def plot_volatility(df: pd.DataFrame, out_path: str, volatility_window: int) -> None: 
    #price and volatility in two axes in the same plot, because they have different scales
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    volatility_col = f'volatility_{volatility_window}'
    fig, ax1 = plt.subplots(figsize=(12,6))
    ax1.plot(df['timestamp'], df['price'], label='Price', color='blue', linewidth=2)
    ax1.set_xlabel('Timestamp')
    ax1.set_ylabel('Price', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax2 = ax1.twinx()
    if volatility_col in df.columns:
        ax2.plot(df['timestamp'], df[volatility_col], label='Volatility', color='red', linewidth=2)
    ax2.set_ylabel('Volatility', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    plt.title('Price and Volatility Over Time')
    fig.tight_layout()
    plt.grid(True)
    plt.legend()
    # Save in png
    plt.savefig(out_path, format='png', dpi = 300, bbox_inches='tight')
    plt.close()

#This is the main function used in the endpoint. It returns a PNG with 3 subplots containing the price and all the analytics contained in the DataFrame (the function itself detects which analytics are present in the DataFrame)
def plot_enriched_price(
    df: pd.DataFrame,
    out_path: str,
    symbol: Symbol | None = None,
    currency: Currency | None = None,
    provider: Provider | None = None,
    price_key: str = "price",
    resample_frequency: ResampleFrequency | None = None,
) -> None:
    """
    Enriched plot in a single PNG.

    Assumes df already comes from compute_enriched_market_chart and therefore
    already contains:
      - pct_change, acum_pct_change
      - rolling_mean_*
      - volatility_*
      - normalized_* columns

    Layout:
      - Subplot 1: price (+ rolling + resampled)
      - Subplot 2: % change + accumulated % change
      - Subplot 3: normalized + volatility (2nd Y axis)

    NOTE: Price is plotted ONLY in the first subplot.
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # ---------- Detect precomputed analytics columns ----------
    # Rolling
    rolling_col: str | None = next(
        (c for c in df.columns if c.startswith("rolling_mean_")), None
    )

    # Volatility
    volatility_col: str | None = next(
        (c for c in df.columns if c.startswith("volatility_")), None
    )

    # Normalized
    norm_col: str | None = next(
        (c for c in df.columns if c.startswith("normalized_")), None
    )

    # Optional resampled series just for visualization (doesn't touch df)
    df_resampled: pd.DataFrame | None = None
    if resample_frequency is not None:
        df_resampled = resample_price_series(
            df[["timestamp", price_key]].copy(),
            price_key,
            resample_frequency,
        )

    # Stats for title
    stats = calculate_stats(df, price_key)

    # ---------- Figure & subplots ----------
    fig, (ax_price, ax_returns, ax_norm) = plt.subplots(3, 1, figsize=(14, 11), sharex=True)

    # =====================================================
    # SUBPLOT 1: Price + Rolling + Resampled
    # =====================================================
    ax_price.plot(
        df["timestamp"], df[price_key],
        label="Price",
        color="black",
        linewidth=1.5,
    )

    if rolling_col is not None and rolling_col in df.columns:
        window_str = rolling_col.split("_")[-1]
        ax_price.plot(
            df["timestamp"], df[rolling_col],
            label=f"Rolling mean ({window_str})",
            linewidth=1.5,
        )

    if df_resampled is not None:
        ax_price.plot(
            df_resampled["timestamp"], df_resampled[price_key],
            label=f"Resampled ({resample_frequency.name})",
            linestyle="--",
            marker="o",
        )

    ax_price.set_ylabel("Price")
    ax_price.set_title("Price, rolling mean & resampled series")
    ax_price.grid(True)
    ax_price.legend(loc="upper left")

    # =====================================================
    # SUBPLOT 2: % change + accumulated return (NO PRICE HERE)
    # =====================================================
    if "pct_change" in df.columns:
        ax_returns.plot(
            df["timestamp"], df["pct_change"],
            label="% change",
            linewidth=1.0,
        )

    if "acum_pct_change" in df.columns:
        ax_returns.plot(
            df["timestamp"], df["acum_pct_change"],
            label="Accumulated % change",
            linewidth=1.5,
        )

    ax_returns.set_ylabel("%")
    ax_returns.set_title("Daily % change & accumulated return")
    ax_returns.grid(True)
    ax_returns.legend(loc="upper left")

    # =====================================================
    # SUBPLOT 3: Normalized + Volatility (NO PRICE HERE)
    # =====================================================
    if norm_col is not None and norm_col in df.columns:
        ax_norm.plot(
            df["timestamp"], df[norm_col],
            label=norm_col,
            linewidth=1.5,
        )

    ax_norm.set_ylabel("Index")
    ax_norm.grid(True)

    if volatility_col is not None and volatility_col in df.columns:
        ax_vol = ax_norm.twinx()
        ax_vol.plot(
            df["timestamp"], df[volatility_col],
            label=volatility_col,
            linewidth=1.0,
            color="red",
            alpha=0.7,
        )
        ax_vol.set_ylabel("Volatility")

        # Combine legends from both Y axes
        l1, lb1 = ax_norm.get_legend_handles_labels()
        l2, lb2 = ax_vol.get_legend_handles_labels()
        ax_norm.legend(l1 + l2, lb1 + lb2, loc="upper left")
    else:
        ax_norm.legend(loc="upper left")

    ax_norm.set_title("Normalized price & volatility")

    # =====================================================
    # Global title with metadata
    # =====================================================
    symbol_str = symbol.name if symbol is not None else ""
    currency_str = currency.name if currency is not None else ""
    provider_str = provider.name if provider is not None else ""

    fig.suptitle(
        (
            f"Enriched analytics — {symbol_str}/{currency_str} | Provider: {provider_str}\n"
            f"min={stats['min_price']:.2f}  "
            f"max={stats['max_price']:.2f}  "
            f"mean={stats['mean_price']:.2f}  "
            f"Total % change={stats['percent_change']:.2f}%"
        ),
        fontsize=13,
    )

    plt.xlabel("Timestamp")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])

    plt.savefig(out_path, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)