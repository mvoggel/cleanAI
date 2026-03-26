# insights.py
# Inefficiency detection engine.
# All outputs are ESTIMATES.

import numpy as np
import pandas as pd
from assumptions import (
    TOKEN_INEFFICIENCY_MULTIPLIER,
    MODEL_OVERUSE_TOKEN_THRESHOLD,
    REPETITION_WINDOW_HOURS,
    HEAVY_TAIL_PERCENTILE,
    MODEL_ENERGY_RATES,
    MODEL_COST_PER_1K,
    REGION_CARBON_INTENSITY,
)


def detect_token_inefficiency(df: pd.DataFrame) -> dict:
    """8A — Flag requests with total_tokens > 2x median."""
    median_tokens = df["total_tokens"].median()
    threshold = median_tokens * TOKEN_INEFFICIENCY_MULTIPLIER
    flagged = df[df["total_tokens"] > threshold]
    pct_requests = len(flagged) / len(df) * 100
    pct_energy = flagged["energy_Wh"].sum() / df["energy_Wh"].sum() * 100
    return {
        "median_tokens": median_tokens,
        "threshold": threshold,
        "count": len(flagged),
        "pct_requests": pct_requests,
        "pct_energy": pct_energy,
        "flagged_df": flagged,
    }


def detect_model_overuse(df: pd.DataFrame) -> dict:
    """8B — Large models doing small tasks (tokens < 500)."""
    large_models = ["gpt-4", "claude"]
    flagged = df[
        df["model"].isin(large_models) &
        (df["total_tokens"] < MODEL_OVERUSE_TOKEN_THRESHOLD)
    ].copy()

    # Energy/cost waste vs. using small-model instead
    sm_energy_rate = MODEL_ENERGY_RATES["small-model"]
    sm_cost_rate = MODEL_COST_PER_1K["small-model"]

    flagged["alt_energy_Wh"] = (flagged["total_tokens"] / 1000) * sm_energy_rate
    flagged["alt_cost_usd"] = (flagged["total_tokens"] / 1000) * sm_cost_rate

    energy_waste = (flagged["energy_Wh"] - flagged["alt_energy_Wh"]).sum()
    cost_waste = (flagged["cost_usd"] - flagged["alt_cost_usd"]).sum()

    return {
        "count": len(flagged),
        "pct_requests": len(flagged) / len(df) * 100,
        "energy_waste_Wh": energy_waste,
        "cost_waste_usd": cost_waste,
        "flagged_df": flagged,
    }


def detect_repetition_waste(df: pd.DataFrame) -> dict:
    """8C — Detect near-duplicate requests within a 1-hour window."""
    df2 = df.copy()
    df2["rounded_input"] = (df2["input_tokens"] / 100).round() * 100
    df2["bucket"] = df2["timestamp"].dt.floor(f"{REPETITION_WINDOW_HOURS}h")
    df2["dedup_key"] = (
        df2["model"] + "|" +
        df2["request_type"] + "|" +
        df2["rounded_input"].astype(str) + "|" +
        df2["bucket"].astype(str)
    )
    dupe_mask = df2.duplicated(subset="dedup_key", keep="first")
    dupes = df2[dupe_mask]
    energy_saveable = dupes["energy_Wh"].sum()
    cost_saveable = dupes["cost_usd"].sum()
    return {
        "count": len(dupes),
        "pct_requests": len(dupes) / len(df) * 100,
        "energy_saveable_Wh": energy_saveable,
        "cost_saveable_usd": cost_saveable,
        "dupe_df": dupes,
    }


def detect_heavy_tail(df: pd.DataFrame) -> dict:
    """8D — Top 10% of requests by energy."""
    threshold = df["energy_Wh"].quantile(HEAVY_TAIL_PERCENTILE)
    top_10 = df[df["energy_Wh"] >= threshold]
    pct_energy = top_10["energy_Wh"].sum() / df["energy_Wh"].sum() * 100
    return {
        "threshold_Wh": threshold,
        "count": len(top_10),
        "pct_energy": pct_energy,
        "top_df": top_10,
    }


def detect_regional_shift(df: pd.DataFrame) -> dict:
    """8E — Carbon savings from shifting Asia workloads to EU."""
    asia_rows = df[df["region"] == "asia"].copy()
    current_carbon_g = asia_rows["carbon_g"].sum()
    eu_intensity = REGION_CARBON_INTENSITY["eu"]
    optimized_carbon_g = asia_rows["energy_kWh"].sum() * eu_intensity
    savings_g = current_carbon_g - optimized_carbon_g
    savings_pct = savings_g / df["carbon_g"].sum() * 100
    return {
        "asia_requests": len(asia_rows),
        "current_carbon_g": current_carbon_g,
        "optimized_carbon_g": optimized_carbon_g,
        "savings_g": savings_g,
        "savings_pct_of_total": savings_pct,
    }


def run_all_insights(df: pd.DataFrame) -> dict:
    return {
        "token_inefficiency": detect_token_inefficiency(df),
        "model_overuse":      detect_model_overuse(df),
        "repetition_waste":   detect_repetition_waste(df),
        "heavy_tail":         detect_heavy_tail(df),
        "regional_shift":     detect_regional_shift(df),
    }
