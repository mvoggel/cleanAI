# data_generator.py
# Generates a simulated dataset of AI API usage requests.
# All outputs are ESTIMATES based on assumed distributions.

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from assumptions import (
    RANDOM_SEED, NUM_ROWS, DAYS_SPAN,
    MODEL_DISTRIBUTION, REGION_DISTRIBUTION, REQUEST_TYPES,
)


def generate_dataset() -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)

    models = list(MODEL_DISTRIBUTION.keys())
    model_weights = list(MODEL_DISTRIBUTION.values())
    regions = list(REGION_DISTRIBUTION.keys())
    region_weights = list(REGION_DISTRIBUTION.values())

    # Timestamps spread over DAYS_SPAN days
    start = datetime(2024, 1, 1)
    seconds_range = DAYS_SPAN * 24 * 3600
    timestamps = [
        start + timedelta(seconds=int(s))
        for s in rng.integers(0, seconds_range, NUM_ROWS)
    ]
    timestamps.sort()

    # Token counts — log-normal for realistic skew
    input_tokens = np.clip(
        rng.lognormal(mean=6.5, sigma=1.0, size=NUM_ROWS).astype(int), 50, 6000
    )
    output_tokens = np.clip(
        rng.lognormal(mean=5.5, sigma=0.9, size=NUM_ROWS).astype(int), 50, 3000
    )

    # ~5% extreme outliers (tokens > 10,000)
    n_outliers = int(NUM_ROWS * 0.05)
    outlier_idx = rng.choice(NUM_ROWS, n_outliers, replace=False)
    input_tokens[outlier_idx] = rng.integers(10_000, 15_001, n_outliers)
    output_tokens[outlier_idx] = rng.integers(3_000, 6_001, n_outliers)

    selected_models = rng.choice(models, size=NUM_ROWS, p=model_weights)
    selected_regions = rng.choice(regions, size=NUM_ROWS, p=region_weights)
    selected_types = rng.choice(REQUEST_TYPES, size=NUM_ROWS)

    df = pd.DataFrame({
        "request_id":    range(1, NUM_ROWS + 1),
        "timestamp":     timestamps,
        "model":         selected_models,
        "input_tokens":  input_tokens,
        "output_tokens": output_tokens,
        "region":        selected_regions,
        "request_type":  selected_types,
    })

    # ~15% near-duplicate requests (caching inefficiency simulation)
    n_dupes = int(NUM_ROWS * 0.15)
    source_idx = rng.choice(NUM_ROWS - 1, n_dupes, replace=True)
    dupe_idx = rng.choice(NUM_ROWS, n_dupes, replace=False)

    for src, dst in zip(source_idx, dupe_idx):
        df.loc[dst, "model"] = df.loc[src, "model"]
        df.loc[dst, "request_type"] = df.loc[src, "request_type"]
        # Round to nearest 100 to simulate "near" duplicate
        rounded = int(round(df.loc[src, "input_tokens"], -2))
        df.loc[dst, "input_tokens"] = max(50, rounded)

    return df
