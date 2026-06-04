"""
utils.py — shared constants, API pull function, and statistics utilities
for the Kalshi FLB analysis pipeline.

Imported by: 02_pull_trades, 03_build_candidate_dataset,
             04_calibration, 05_exploitability, 06_figures_tables
"""

import requests
import pandas as pd
import time
from scipy import stats as scipy_stats

# ── Kalshi API ────────────────────────────────────────────────────────────────
BASE_URL  = 'https://api.elections.kalshi.com/trade-api/v2'
KEEP_COLS = ['trade_id', 'ticker', 'created_time', 'count_fp',
             'yes_price_dollars', 'no_price_dollars', 'taker_side']


def get_historical_trades(ticker, max_pages=None, verbose=False):
    """Paginate /historical/trades for ticker; return DataFrame."""
    all_trades = []
    cursor = None
    page = 0
    while True:
        params = {'ticker': ticker, 'limit': 1000}
        if cursor:
            params['cursor'] = cursor
        r = requests.get(f'{BASE_URL}/historical/trades', params=params)
        if r.status_code != 200:
            if verbose:
                print(f'  Error {r.status_code}: {r.text[:200]}')
            break
        data   = r.json()
        trades = data.get('trades', [])
        all_trades.extend(trades)
        page  += 1
        cursor = data.get('cursor')
        if not cursor or len(trades) == 0:
            break
        if max_pages and page >= max_pages:
            break
    if verbose:
        print(f'  done: {len(all_trades):,} trades for {ticker}')
    return pd.DataFrame(all_trades)


# ── Analysis constants ────────────────────────────────────────────────────────
RNG_SEED  = 42
BOOT_REPS = 2000
FEE_RATE  = 0.07    # Kalshi taker-fee multiplier: 0.07 × P × (1-P) per contract
FLOOR_MAX = 0.02    # at_floor flag: YES price <= this
LS_MAX    = 0.15    # longshot upper bound (exclusive)
FAV_MIN   = 0.50    # favorite lower bound (exclusive)
C_GRID    = [0.000, 0.005, 0.010, 0.015, 0.020]  # spread cost sensitivity grid


# ── Statistics ────────────────────────────────────────────────────────────────
def clopper_pearson_upper(n_total, alpha=0.05):
    """One-sided upper Clopper-Pearson bound for zero successes.
    Returns Beta(1-alpha; 1, n_total) = 1 - alpha^(1/n_total).
    Use for buckets / bands with n_wins == 0 (bootstrap is degenerate there).
    """
    if n_total == 0:
        return float('nan')
    return float(scipy_stats.beta.ppf(1 - alpha, 1, n_total))


# ── Plot palette and typography ───────────────────────────────────────────────
C_LONGSHOT  = '#E69F00'   # orange  — longshots / significant results
C_FAVORITE  = '#009E73'   # teal green — favorites
C_POLITICAL = '#0072B2'   # blue — political domain
C_MUTED     = '#CCCCCC'   # light grey — floored / not significant
C_DIAGONAL  = '#444444'   # 45-degree perfectly-priced diagonal

FL = 20   # axis-label font size
FT = 15   # tick-label font size
FA = 16   # annotation / row-label font size
