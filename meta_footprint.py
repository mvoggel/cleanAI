# meta_footprint.py
# Estimates the carbon cost of building cleanAI itself.
# A transparency and integrity feature — all outputs are ESTIMATES.

from assumptions import (
    META_ENERGY_PER_INTERACTION_Wh,
    META_DEV_INTERACTIONS,
    META_BUILD_REGION,
    REGION_CARBON_INTENSITY,
)


def compute_meta_footprint() -> dict:
    total_energy_Wh = META_DEV_INTERACTIONS * META_ENERGY_PER_INTERACTION_Wh
    total_energy_kWh = total_energy_Wh / 1000
    carbon_intensity = REGION_CARBON_INTENSITY[META_BUILD_REGION]
    total_carbon_g = total_energy_kWh * carbon_intensity
    total_carbon_kg = total_carbon_g / 1000

    # Context equivalents (approximate)
    # Average car emits ~120 gCO2/km
    km_driven_equiv = total_carbon_g / 120
    # Average smartphone charge ~8.22 Wh, ~4 gCO2 at us-east intensity
    phone_charges_equiv = total_carbon_g / 4

    return {
        "interactions": META_DEV_INTERACTIONS,
        "energy_per_interaction_Wh": META_ENERGY_PER_INTERACTION_Wh,
        "build_region": META_BUILD_REGION,
        "carbon_intensity_gCO2_kWh": carbon_intensity,
        "total_energy_Wh": total_energy_Wh,
        "total_energy_kWh": total_energy_kWh,
        "total_carbon_g": total_carbon_g,
        "total_carbon_kg": total_carbon_kg,
        "km_driven_equiv": km_driven_equiv,
        "phone_charges_equiv": phone_charges_equiv,
    }
