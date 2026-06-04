# Favorite-Longshot Bias in Kalshi Prediction Markets

Tests whether Kalshi markets systematically overprice longshot candidates
across a population of 98 discrete-entity, multi-candidate events (sports + political).
The central finding is that above-floor longshots (2–15¢ implied probability)
are overpriced — ~6¢ implied vs ~2.5% realized win rate — and the overpricing
is economically exploitable via a buy-NO strategy at zero spread cost.

---

## Run order

Steps 00–02 hit the Kalshi API and are needed only for a fresh data pull.
Steps 03–06 run on cached data and reproduce all findings, figures, and tables.

### [00_pull_kalshi_metadata.ipynb](code/00_pull_kalshi_metadata.ipynb)

**Takes in:**
- Kalshi REST API (`/markets` and `/events` endpoints) — no API key required for public market data
- Cached output if re-running: `data/markets_metadata.csv`

**What it does:**
- Pages through the Kalshi `/markets` and `/events` endpoints
- Joins market records to event records on `event_ticker`
- Saves a flat metadata table covering all available markets

**Outputs:**
- `data/markets_metadata.csv` — one row per Kalshi sub-market with event metadata

---

### [01_build_event_universe.ipynb](code/01_build_event_universe.ipynb)

**Takes in:**
- `data/markets_metadata.csv` (written by step 00)

**What it does:**
- Applies pre-registered inclusion filters: ≥4 sub-markets per event, ≥500 trades,
  exactly 1 YES winner, all sub-markets finalized, and exclusion of noisy ticker
  prefixes (KXMVE, KXTRUTHSOCIAL)
- Produces the canonical event universe used in all downstream analysis

**Outputs:**
- `data/event_universe.csv` — one row per qualifying event (122 events before discrete-entity filter)

---

### [02_pull_trades.ipynb](code/02_pull_trades.ipynb)

**Takes in:**
- `data/event_universe.csv` (written by step 01)
- `data/markets_metadata.csv` (written by step 00)
- Kalshi REST API (`/historical/trades` endpoint via `utils.get_historical_trades`)

**What it does:**
- Iterates over every sub-market ticker in the event universe
- Downloads the full trade-level history (paginated, 1,000 trades per page) for each
- Skips tickers whose file already exists (safe to re-run)

**Outputs:**
- `data/kx*_trades.csv` — one CSV per sub-market (~1,715 files), each containing
  trade ID, timestamp, contract count, YES/NO prices in dollars, and taker side

---

### [03_build_candidate_dataset.ipynb](code/03_build_candidate_dataset.ipynb)

**Takes in:**
- `data/event_universe.csv` (written by step 01)
- `data/markets_metadata.csv` (written by step 00)
- `data/kx*_trades.csv` (written by step 02)

**What it does:**
- Detects `t_resolve` per event as the first moment the winner's YES price durably
  crosses 0.90 (stays above 0.85 thereafter); falls back to settlement timestamp
  for thin-market events
- Sets a snapshot 24 hours before `t_resolve`
- Extracts the last pre-snapshot trade price per candidate
- Audits winner flags and applies the discrete-entity refinement (excludes 24
  numeric-range events such as seat-count brackets and margin bins)
- Flags at-floor candidates (YES price ≤ 2¢) and above-floor longshots (2–15¢)

**Outputs:**
- `data/candidate_level_full.csv` — intermediate dataset, 122 events including numeric-range
- `data/candidate_level_discrete.csv` — canonical analysis dataset, 98 discrete-entity events
- `output/buckets_overall_cw_discrete.csv` and related `output/buckets_*_discrete.csv` — pre-computed calibration bucket tables

---

### [04_calibration.ipynb](code/04_calibration.ipynb)

**Takes in:**
- `data/candidate_level_discrete.csv` (written by step 03)

**What it does:**
- Tests for a domain gap in overpricing between sports and political events
- Runs favorites-band calibration (>50¢) with sub-band breakdown
- Runs fine-grained calibration across 9 price bands from floor to 1.00
- Uses event-clustered block bootstrap (2,000 reps, `RNG_SEED=42`) for inference;
  uses Clopper-Pearson upper bound for zero-winner bands

**Outputs:**
- Console / printed table output only (no files written)

---

### [05_exploitability.ipynb](code/05_exploitability.ipynb)

**Takes in:**
- `data/candidate_level_discrete.csv` (written by step 03)

**What it does:**
- Simulates a buy-NO strategy on all above-floor longshots (2–15¢)
- Computes net edge over a sensitivity grid of spread costs
  c ∈ {0, 0.5, 1.0, 1.5, 2.0}¢
- Models the Kalshi taker fee (`FEE_RATE = 0.07 × P × (1–P)` per contract)
- Identifies breakeven spread cost c\*
- Runs a drop-dominant-event robustness check

**Outputs:**
- Console / printed table output only (no files written)

---

### [06_figures_tables.ipynb](code/06_figures_tables.ipynb)

**Takes in:**
- `data/candidate_level_discrete.csv` (written by step 03)
- `output/buckets_overall_cw_discrete.csv` (written by step 03)

**What it does:**
- Generates all four paper figures using the shared plot palette from `utils.py`

**Outputs:**
- `output/fig_calibration_slide3.pdf` / `.png` — full calibration chart across all 9 price bands
- `output/fig_calibration_zoom.pdf` / `.png` — zoomed calibration for the longshot and favorite regions
- `output/fig_exploitability.pdf` / `.png` — net-edge sensitivity grid over spread costs
- `output/fig_domain_calibration.pdf` / `.png` — sports vs. political domain comparison

---

## Shared utilities: [utils.py](code/utils.py)

Imported by notebooks 02–06.

- `get_historical_trades(ticker)` — paginates the Kalshi `/historical/trades` endpoint and returns a DataFrame
- `clopper_pearson_upper(n_total)` — one-sided upper Clopper-Pearson bound for zero-winner buckets
- Analysis constants: `RNG_SEED=42`, `BOOT_REPS=2000`, `FEE_RATE=0.07`, `FLOOR_MAX=0.02`, `LS_MAX=0.15`, `FAV_MIN=0.50`, `C_GRID`
- Plot palette: `C_LONGSHOT` (orange), `C_FAVORITE` (teal), `C_POLITICAL` (blue), `C_MUTED` (grey), `C_DIAGONAL` (dark grey)

---

## Directory layout

```
code/
  utils.py                          shared utilities and constants
  00_pull_kalshi_metadata.ipynb     step 00 — API pull
  01_build_event_universe.ipynb     step 01 — filter universe
  02_pull_trades.ipynb              step 02 — download trade CSVs
  03_build_candidate_dataset.ipynb  step 03 — build analysis dataset
  04_calibration.ipynb              step 04 — calibration analysis
  05_exploitability.ipynb           step 05 — exploitability analysis
  06_figures_tables.ipynb           step 06 — all paper figures

data/
  markets_metadata.csv              written by 00
  event_universe.csv                written by 01
  candidate_level_full.csv          written by 03 (intermediate, 122 events)
  candidate_level_discrete.csv      written by 03 (canonical, 98 discrete-entity events)
  kx*_trades.csv                    written by 02 (one file per sub-market, ~1,715 files)

output/
  buckets_*_discrete.csv            written by 03 (calibration bucket tables)
  fig_calibration_slide3.pdf/png    written by 06
  fig_calibration_zoom.pdf/png      written by 06
  fig_exploitability.pdf/png        written by 06
  fig_domain_calibration.pdf/png    written by 06

archive/                            superseded notebooks and data (do not run)
```

---

## Key methodology notes

- **Snapshot price**: last trade strictly before `t_resolve − 24 h`, where `t_resolve` is the
  first moment the winner's YES price durably crossed 0.90 (stays above 0.85 thereafter).
  Fallback to settlement timestamp for thin-market events where the winner never crossed.
- **Floored candidates** (≤2¢): the Kalshi $0.01 minimum tick mechanically overprices
  these. They are reported separately and excluded from the behavioral FLB claim.
- **Above-floor longshots** (2–15¢): the behavioral test zone. The FLB finding rests
  entirely on this band.
- **Inference**: event-clustered block bootstrap (2,000 reps, resample events not candidates).
  Zero-winner bands use Clopper-Pearson upper bound (bootstrap is degenerate there).
- **Discrete-entity filter**: 24 numeric-range events (seat-count brackets, margin bins)
  are excluded from the primary analysis (`candidate_level_discrete.csv`).
