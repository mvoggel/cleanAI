# cleanAI — AI Efficiency & Carbon Insight Tool

> All outputs are estimates. See `assumptions.py` for all constants.

A lightweight, locally-runnable research prototype that acts as a "Google Analytics layer for AI usage" — adding estimated energy consumption, carbon emissions, inefficiency detection, and optimization recommendations on top of AI API usage data.

## Setup

```bash
# 1. Create and activate the virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

## Project Structure

```
cleanAI/
├── app.py              # Streamlit dashboard (5 tabs)
├── assumptions.py      # All constants — energy rates, carbon intensity, costs
├── data_generator.py   # Simulated 7,500-row dataset (seed=42)
├── processing.py       # Per-request energy / carbon / cost calculations
├── insights.py         # Inefficiency detection (token waste, model overuse, caching, heavy tail, regional shift)
├── optimizer.py        # Before/after scenarios (model downgrade, token reduction, caching)
├── meta_footprint.py   # Carbon cost of building this tool
├── requirements.txt
└── README.md
```

## Dashboard Tabs

| Tab | Contents |
|-----|----------|
| Overview | KPI cards, energy-over-time chart, summary stats |
| Breakdown | Energy / carbon / cost by model, region, request type |
| Inefficiencies | 5 detection modules with counts and impact estimates |
| Optimization Scenarios | Before/after comparison for 3 scenarios |
| Meta Footprint | Carbon cost of building cleanAI |

## Key Assumptions

All assumptions live in `assumptions.py`. Nothing is hardcoded elsewhere.

- Energy rates sourced from Luccioni et al. 2023 and ML CO2 Impact Calculator
- Carbon intensity from Electricity Maps regional averages
- Cost rates approximate public API pricing

## v2 Ideas

- Swap simulated data for real OpenAI / Anthropic usage CSV exports
- Pull live carbon intensity from Electricity Maps API
- Add Helicone integration for real-time token logging
