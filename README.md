# The NFL Running Back Value Debate

This project investigates whether NFL running backs are undervalued and whether that is justifed through the analysis between performance metrics, contracts, and team success.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Fetch team stats from ESPN API
python -m src.api.espn_nfl --season 2024 --save data/espn_team_stats_2024.json
