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

Update 11/30 : Visuals have been dropped for clustering. Visualization could work, but was proving to be a moot visual overall and hard to comprehend. Some things that I would change moving forward and given another semester to work on this project

1. Choose a smaller sample size of years for running backs SO I could get statistics for recievers and compare those.

2. Likely not use PFR at all and waste time trying to scrape there when there is kaggle api that is accessible

3. IF NOT USING RECIEVER DATA - reduce scope to not look at passing production at all, as this point does correlate, but there are more recievers than running backs typically seeing the ball per game. There could be an angle where because there are X recievers active and running routes vs 1-2 running backs on the field (with one typically on the field at a time) running backs are put at a disadvantage.

4. Look at recieving running backs to assess value as running backs such as Jonathan Taylor, CMC, DeVon Achane and others who ARE used in the passing game should carry signifacntly more weight than those that do not participate as much.

5. Utilize different or more advanced models to help assist in the future. There is a lot of plug and chugging and backtracking (which is seen in the .ipynb) and also some of the .py are redundant due to how wide the scope was. If the scope was reduced earlier on and established specific running backs (rather than using 70+ carries [which excludes the fact that some starters carry for less than 70 and SHOULD be accounted in their contract valuation]) There is a lot of different angles that need to be taken that I would not be able to fully break down and get the best conclusions in a 15 week span. I found the right conclusions, but I feel the data is a bit skewed and biased, and I would want to really dig into specific players i.e. 50 running backs per year over a few specific periods of time. 

When Using .ipynb - use .../src/PlayerANDTeam.ipynb (to merge player and team data) and then run results.ipynb

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
