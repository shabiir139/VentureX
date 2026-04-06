# ─── VentureX · Startup Simulation ──────────────────────────────────────────
"""
Manages startup stage progression from IDEA → MVP → MARKET_TEST → GROWTH → SCALE.
Handles funding rounds, burn rate tracking, pivots, and MVP scoring.
"""
from __future__ import annotations
import random
from src.constants import STAGES, STAGE_ORDER


def get_stage_info(stage: str) -> dict:
    """Get configuration for a stage."""
    return STAGES.get(stage, STAGES["IDEA"])


def check_stage_progression(
    stage: str,
    days_in_stage: int,
    cash: float,
    revenue: float,
    market_share: float,
    customer_satisfaction: float,
) -> tuple[bool, str]:
    """
    Check if the startup should progress to the next stage.
    Returns (should_advance, reason).
    """
    info = get_stage_info(stage)
    idx = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else 0

    # Must spend minimum days in stage
    if days_in_stage < info["min_days"]:
        return False, f"Need {info['min_days'] - days_in_stage} more days in {info['label']}"

    # Already at final stage
    if idx >= len(STAGE_ORDER) - 1:
        return False, "Already at SCALE stage — final stage reached"

    next_stage = STAGE_ORDER[idx + 1]
    next_info = get_stage_info(next_stage)

    # Stage-specific advancement criteria
    criteria_met = False
    reason = ""

    if stage == "IDEA":
        # Need a basic plan (simulated by days + any revenue attempt)
        criteria_met = days_in_stage >= info["min_days"]
        reason = "Idea validated — ready to build MVP"

    elif stage == "MVP":
        # Need to show product viability
        criteria_met = revenue > 0 and customer_satisfaction > 0.4
        reason = f"MVP shows revenue (${revenue:,.0f}) and satisfaction ({customer_satisfaction:.0%})"

    elif stage == "MARKET_TEST":
        # Need market traction
        criteria_met = (
            revenue > 5_000
            and market_share > 0.07
            and customer_satisfaction > 0.5
        )
        reason = f"Market traction: share={market_share:.1%}, revenue=${revenue:,.0f}"

    elif stage == "GROWTH":
        # Need significant growth
        criteria_met = (
            revenue > 50_000
            and market_share > 0.15
            and cash > 100_000
        )
        reason = f"Growth targets met: revenue=${revenue:,.0f}, share={market_share:.1%}"

    if criteria_met:
        return True, reason
    else:
        return False, f"Criteria not yet met for {next_info['label']}"


def advance_stage(current_stage: str) -> tuple[str, str]:
    """
    Advance to the next stage.
    Returns (new_stage, stage_label).
    """
    idx = STAGE_ORDER.index(current_stage) if current_stage in STAGE_ORDER else 0
    if idx < len(STAGE_ORDER) - 1:
        new_stage = STAGE_ORDER[idx + 1]
        return new_stage, STAGES[new_stage]["label"]
    return current_stage, STAGES[current_stage]["label"]


def process_funding_round(
    stage: str,
    cash: float,
    total_funding: float,
    market_share: float,
    revenue: float,
    funding_multiplier: float = 1.0,
) -> tuple[float, str]:
    """
    Attempt to raise funding based on current stage and metrics.
    Returns (amount_raised, description).
    """
    info = get_stage_info(stage)
    max_funding = info["funding_unlock"]

    if max_funding <= 0:
        return 0, "Too early for funding — complete ideation first"

    # Valuation factors
    traction_score = min(1.0, (revenue / max(max_funding * 0.1, 1)) * 0.5 + market_share * 5)
    success_probability = 0.3 + traction_score * 0.5  # 30-80% chance

    # Apply scenario modifier
    success_probability *= funding_multiplier

    if random.random() > success_probability:
        return 0, f"Funding round unsuccessful (probability was {success_probability:.0%}). Improve traction."

    # Random portion of max funding
    amount = max_funding * random.uniform(0.3, 0.8) * funding_multiplier
    amount = round(amount, -3)  # Round to nearest $1k

    return amount, (
        f"🎉 Raised ${amount:,.0f} in funding! "
        f"(Stage: {info['label']}, Traction score: {traction_score:.0%})"
    )


def process_pivot(
    stage: str,
    market_share: float,
    satisfaction: float,
) -> tuple[float, float, str]:
    """
    Execute a strategic pivot. Resets some progress but opens new opportunities.
    Returns (new_market_share, new_satisfaction, description).
    """
    # Pivoting costs market share but can improve satisfaction if market was bad
    share_loss = market_share * random.uniform(0.2, 0.5)
    sat_change = random.uniform(-0.1, 0.2)  # Could go either way

    new_share = max(0.01, market_share - share_loss)
    new_sat = max(0.1, min(1.0, satisfaction + sat_change))

    return new_share, new_sat, (
        f"Pivoted strategy. Market share: {market_share:.1%} → {new_share:.1%}. "
        f"Satisfaction: {satisfaction:.0%} → {new_sat:.0%}. "
        f"New market position established."
    )


def calculate_mvp_score(
    revenue: float,
    customers: float,
    satisfaction: float,
    days_to_mvp: int,
) -> float:
    """
    Score MVP success from 0.0 to 1.0.
    Considers revenue, customer base, satisfaction, and speed.
    """
    rev_score = min(1.0, revenue / 10_000)
    cust_score = min(1.0, customers / 1000)
    speed_score = max(0, 1.0 - (days_to_mvp - 5) / 20)

    return round(
        rev_score * 0.3 + cust_score * 0.2 + satisfaction * 0.3 + speed_score * 0.2, 3
    )
