# assumptions.py
# All constants are defined here — nothing is hardcoded elsewhere.
# All outputs from this tool are ESTIMATES.

# Energy consumption per 1,000 tokens (Wh)
MODEL_ENERGY_RATES = {
    "gpt-4":       0.5,
    "gpt-3.5":     0.2,
    "claude":      0.4,
    "small-model": 0.1,
}

# Carbon intensity by region (gCO2 per kWh)
REGION_CARBON_INTENSITY = {
    "us-east": 400,
    "us-west": 300,
    "eu":      250,
    "asia":    500,
}

# Approximate cost per 1,000 tokens (USD)
MODEL_COST_PER_1K = {
    "gpt-4":       0.030,
    "gpt-3.5":     0.002,
    "claude":      0.015,
    "small-model": 0.001,
}

# Meta footprint — carbon cost of building cleanAI itself
META_ENERGY_PER_INTERACTION_Wh = 5       # Wh per AI interaction (midpoint of 2–10 Wh range)
META_DEV_INTERACTIONS = 200              # Number of dev interactions (midpoint of 100–300)
META_BUILD_REGION = "us-east"            # Region where development happened

# Dataset generation
RANDOM_SEED = 42
NUM_ROWS = 7500
DAYS_SPAN = 90

# Model distribution weights
MODEL_DISTRIBUTION = {
    "gpt-4":       0.35,
    "gpt-3.5":     0.30,
    "claude":      0.25,
    "small-model": 0.10,
}

# Region distribution weights
REGION_DISTRIBUTION = {
    "us-east": 0.40,
    "us-west": 0.25,
    "eu":      0.20,
    "asia":    0.15,
}

REQUEST_TYPES = ["chat", "classification", "embedding", "agent-loop"]

# Insight thresholds
TOKEN_INEFFICIENCY_MULTIPLIER = 2        # Flag requests > 2x median total tokens
MODEL_OVERUSE_TOKEN_THRESHOLD = 500      # Large model on small task if tokens < this
REPETITION_WINDOW_HOURS = 1              # Time window for duplicate detection
HEAVY_TAIL_PERCENTILE = 0.90            # Top 10% by energy

# Optimizer scenarios
DOWNGRADE_FRACTION = 0.30               # 30% of gpt-4 calls downgraded
TOKEN_REDUCTION_FACTOR = 0.25           # 25% token reduction
