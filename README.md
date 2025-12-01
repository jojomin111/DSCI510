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

# Data Sources

Pro Football Reference
Individual player stats including Rushing yards, attempts, touchdowns, yards per carry, fumbles, longest rush, yards per game, and the year 
Collected via Kaggle API into CSV; The stats are used to measure a player’s on-field performance using basic metrics
Kaggle API / CSV

OverTheCap
Player contract stats (with inflation considered) which include the year signed, total contract, signing bonus, average per year 
Collected via web scraping; this contract data shows how much a player is valued at, this will help to determine value
Web Scraping .CSV

ESPN
Team-level stats from years 2001-2024, this will include wins and losses as well as team total passing and rushing yards
Scraped ESPN’s public API; this took all season stats per team from the years 2001-2024 to find the season outcomes as well as offensive stats.
Web Scraping .JSON

## Analysis

I used various models such as line charts, LOWESS, Scatter plots, Heatmaps, and a histogram in order to visualize running back efficiency and stats. 

## Summary of Results

I used line charts to show the decline in running back earnings per year (with inflation adjusted numbers) from 2001-2024 this is in order to establish the narrative that running backs are losing value. 

I used a scatter plot to show the relation between running back age and efficiency and I utilized LOWESS chart to show the running back APY by age and ALSO to represent the drop off in number of running backs in the league past a certain age since the trend line showed an increase around 26-27 (which is an age that running backs are typically signed onto contracts following the conclusion of their rookie deals)

I used scatter plots to show the relation of rushing yards and passing yards to wins per team. And I also used a heat map to show correlations between various running back stats and wins and apy - this would go on to prove salary is tied to volume rather than efficiency.

Finally I used a histogram to represent the decline after contract years which helps to drive the narrative that running backs are overvalued. 

I answered the main question that I first sought to answer which was "Are running backs declining in production and value?" and then I had the hypothesis that was running backs are declining because there is just a lack of success from running backs when comparing price to success ratio - and I believe that the conclusion that is made is running backs decline with age (and I would have liked to compare this to recievers to get a true conclusion here) and that their output does not have a strong correlation to a winning team. I think that if I had time (which I tried but with the holiday I was unable to do more analysis) I would change the scope maybe even further to evaluate "Are running backs worth signing past rookie deals, or should teams just sign rookie running backs and continue to draft new talent for the low prices?" I think that rookie deals are often a very strong price->success and veterans often fall short of that with very few exceptions. 

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
