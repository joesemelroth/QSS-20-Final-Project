# QSS-20-Final-Project

This project compares trading activity and price discovery in Kalshi prediction markets
with structurally different information environments: sports events, where outcome
information arrives publicly in real time, and political events, where information is
privately held until a discrete announcement. The motivating case study pairs the 2026
College Football Playoff National Championship (`KXNCAAF-26-IND`) with the market for
Trump's Fed Chair nominee, won by Kevin Warsh (`KXFEDCHAIRNOM-29-KW`).

## Order to run

1. [pull_data.ipynb](QSS%2020%20Final%20Project/code/pull_data.ipynb)

* Takes in:
   * Kalshi's public REST API (`https://api.elections.kalshi.com/trade-api/v2`)
   * Market tickers: `KXNCAAF-26-IND` (Indiana wins CFP championship) and `KXFEDCHAIRNOM-29-KW` (Warsh nominated as Fed Chair)
* What it does:
   * Locates the target events and confirms the market tickers via the `/events` and `/historical/markets` endpoints
   * Defines a pull function against the `/historical/trades` endpoint
   * Pulls all trades for each market and trims to the analysis columns (`trade_id`, `ticker`, `created_time`, `count_fp`, `yes_price_dollars`, `no_price_dollars`, `taker_side`)
* Outputs:
   * Two .csv files, each containing trade-level data for one market:
      1. [indiana_championship_trades.csv](QSS%2020%20Final%20Project/data/indiana_championship_trades.csv)
      2. [warsh_fed_chair_trades.csv](QSS%2020%20Final%20Project/data/warsh_fed_chair_trades.csv)

2. [analyze.ipynb](QSS%2020%20Final%20Project/code/analyze.ipynb)

* Takes in:
   * The two .csv files created in step 1
* What it does:
   * Loads the trades, forces numeric types on prices/sizes, and parses timestamps
   * Re-centers each market on its verified information event (final whistle at ~11:16 PM ET Jan 19, 2026 for Indiana; Trump's Truth Social post at 6:48 AM ET Jan 30, 2026 for Warsh) and restricts to a window of −16 to +5 hours around it
   * Computes trading activity per 15-minute bin (normalized to each market's peak) for the activity figure
   * Computes volume-weighted average price (VWAP) per 10-minute bin for the price figure
   * Marks secondary reference points: the Bloomberg report (9:17 PM ET Jan 29) and kickoff (7:30 PM ET Jan 19)
* Outputs:
   * Two .png figures:
      1. [trading_activity_final.png](QSS%2020%20Final%20Project/output/trading_activity_final.png) — normalized trading activity around each market's information event
      2. [price_trajectory.png](QSS%2020%20Final%20Project/output/price_trajectory.png) — implied probability over time, showing when each market reached certainty
