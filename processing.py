# processing.py
# Computes per-request energy, carbon, and cost fields.
# All outputs are ESTIMATES.

import pandas as pd
from assumptions import MODEL_ENERGY_RATES, REGION_CARBON_INTENSITY, MODEL_COST_PER_1K


def compute_per_request(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["total_tokens"] = df["input_tokens"] + df["output_tokens"]
    df["energy_Wh"] = (df["total_tokens"] / 1000) * df["model"].map(MODEL_ENERGY_RATES)
    df["energy_kWh"] = df["energy_Wh"] / 1000
    df["carbon_g"] = df["energy_kWh"] * df["region"].map(REGION_CARBON_INTENSITY)
    df["cost_usd"] = (df["total_tokens"] / 1000) * df["model"].map(MODEL_COST_PER_1K)
    return df


def compute_aggregations(df: pd.DataFrame) -> dict:
    totals = {
        "total_requests":     len(df),
        "total_energy_Wh":    df["energy_Wh"].sum(),
        "total_energy_kWh":   df["energy_kWh"].sum(),
        "total_carbon_g":     df["carbon_g"].sum(),
        "total_carbon_kg":    df["carbon_g"].sum() / 1000,
        "total_cost_usd":     df["cost_usd"].sum(),
        "avg_energy_Wh":      df["energy_Wh"].mean(),
        "avg_carbon_g":       df["carbon_g"].mean(),
        "avg_cost_usd":       df["cost_usd"].mean(),
    }

    def breakdown(group_col):
        g = df.groupby(group_col).agg(
            energy_Wh=("energy_Wh", "sum"),
            carbon_g=("carbon_g", "sum"),
            cost_usd=("cost_usd", "sum"),
            requests=("request_id", "count"),
        ).reset_index()
        g["energy_pct"] = g["energy_Wh"] / totals["total_energy_Wh"] * 100
        g["carbon_pct"] = g["carbon_g"] / totals["total_carbon_g"] * 100
        g["cost_pct"] = g["cost_usd"] / totals["total_cost_usd"] * 100
        return g

    totals["by_model"] = breakdown("model")
    totals["by_region"] = breakdown("region")
    totals["by_request_type"] = breakdown("request_type")

    return totals
