# optimizer.py
# Scenario simulations — before/after comparisons.
# All outputs are ESTIMATES.

import numpy as np
import pandas as pd
from assumptions import (
    RANDOM_SEED, DOWNGRADE_FRACTION, TOKEN_REDUCTION_FACTOR,
    MODEL_ENERGY_RATES, REGION_CARBON_INTENSITY, MODEL_COST_PER_1K,
)
from insights import detect_repetition_waste


def _recalc(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["total_tokens"] = df["input_tokens"] + df["output_tokens"]
    df["energy_Wh"] = (df["total_tokens"] / 1000) * df["model"].map(MODEL_ENERGY_RATES)
    df["energy_kWh"] = df["energy_Wh"] / 1000
    df["carbon_g"] = df["energy_kWh"] * df["region"].map(REGION_CARBON_INTENSITY)
    df["cost_usd"] = (df["total_tokens"] / 1000) * df["model"].map(MODEL_COST_PER_1K)
    return df


def _summarize(df: pd.DataFrame) -> dict:
    return {
        "energy_Wh":  df["energy_Wh"].sum(),
        "carbon_g":   df["carbon_g"].sum(),
        "cost_usd":   df["cost_usd"].sum(),
    }


def _savings(before: dict, after: dict) -> dict:
    result = {}
    for k in before:
        result[f"saved_{k}"] = before[k] - after[k]
        result[f"saved_{k}_pct"] = (before[k] - after[k]) / before[k] * 100
    return result


def scenario_model_downgrade(df: pd.DataFrame) -> dict:
    """Scenario 1 — Replace 30% of gpt-4 calls with small-model."""
    rng = np.random.default_rng(RANDOM_SEED)
    gpt4_idx = df.index[df["model"] == "gpt-4"].tolist()
    n_downgrade = int(len(gpt4_idx) * DOWNGRADE_FRACTION)
    chosen = rng.choice(gpt4_idx, n_downgrade, replace=False)

    after_df = df.copy()
    after_df.loc[chosen, "model"] = "small-model"
    after_df = _recalc(after_df)

    before = _summarize(df)
    after = _summarize(after_df)
    return {"before": before, "after": after, "savings": _savings(before, after),
            "n_affected": n_downgrade}


def scenario_token_reduction(df: pd.DataFrame) -> dict:
    """Scenario 2 — Reduce all tokens by 25% (prompt optimisation)."""
    after_df = df.copy()
    after_df["input_tokens"] = (after_df["input_tokens"] * (1 - TOKEN_REDUCTION_FACTOR)).astype(int)
    after_df["output_tokens"] = (after_df["output_tokens"] * (1 - TOKEN_REDUCTION_FACTOR)).astype(int)
    after_df = _recalc(after_df)

    before = _summarize(df)
    after = _summarize(after_df)
    return {"before": before, "after": after, "savings": _savings(before, after),
            "reduction_pct": TOKEN_REDUCTION_FACTOR * 100}


def scenario_caching(df: pd.DataFrame) -> dict:
    """Scenario 3 — Remove all duplicate requests (caching)."""
    rep = detect_repetition_waste(df)
    dupe_ids = rep["dupe_df"].index
    after_df = df.drop(index=dupe_ids)
    after_df = _recalc(after_df)

    before = _summarize(df)
    after = _summarize(after_df)
    return {"before": before, "after": after, "savings": _savings(before, after),
            "dupes_removed": rep["count"]}


def run_all_scenarios(df: pd.DataFrame) -> dict:
    return {
        "model_downgrade":  scenario_model_downgrade(df),
        "token_reduction":  scenario_token_reduction(df),
        "caching":          scenario_caching(df),
    }
