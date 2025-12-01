# The NFL Running Back Value Debate

This project investigates whether NFL running backs are undervalued and whether that is justifed through the analysis between performance metrics, contracts, and team success.

This project analyzes:

Do running back contracts match their production?

Does running back performance correlate with team wins?

Are teams justified in paying RBs less than WRs/QBs?

How do RBs age and decline over time?

Which RBs are overpaid or underpaid relative to performance?

The project uses data from:

ESPN API (team stats 2000–2024)
Pro Football Reference (rushing stats 2001–2024) (SWAPPED OUT WITH KAGGLE.API)
OverTheCap (inflation-adjusted RB contracts)

## Run Tests

pytest src/tests.py

## Quick Start

```bash
python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

#src/api/espn.py
python -m src.api.espn_nfl --season 2024 --save data/espn_team_stats_2024.json

#src/scrapers/otc_rb_contracts.py
python -m src.scrapers.otc_rb_contracts --save data/otc_rb_contracts_raw.csv

#src/prep_rushing_all.py
python -m src.prep_rushing_all --input data/rushing_cleaned.csv --save data/rushing_clean_final.csv

#src/prep_otc_filter_rb70.py
python -m src.prep_otc_filter_rb70 --contracts data/otc_rb_contracts_raw.csv --rushing data/rushing_clean.csv --save data/otc_rb_contracts_rb70.csv

#src/prep_fix_rushing_teams.py
python -m src.prep_fix_rushing_teams --input data/rb_rushing_fixed.csv --save data/rb_rushing_fixed_clean.csv

#Final merge of data 
python src/main.py --task merge --out data/final_rb_analysis_master.csv

## When Using .ipynb - use .../src/PlayerANDTeam.ipynb (to merge player and team data) and then run results.ipynb
