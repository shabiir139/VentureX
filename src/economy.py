# ─── VentureX · Economy Engine ──────────────────────────────────────────────
"""
Simulates market dynamics: supply/demand, price elasticity, competition.
"""
from __future__ import annotations
import random
import math
from src.models import MarketState
from src.constants import MARKET


def update_market(
    market: MarketState,
    day: int,
    marketing_effectiveness: float = 0.5,
    product_quality: float = 0.5,
    price_change: float = 0.0,
    expand_market: bool = False,
    demand_multiplier: float = 1.0,
) -> str:
    """
    Update market conditions for the day.
    Returns a summary of market changes.
    """
    changes = []

    # ── Price adjustment ──
    if price_change != 0:
        old_price = market.price
        market.price = max(10.0, market.price + price_change)
        changes.append(f"Price: ${old_price:.0f} → ${market.price:.0f}")

    # ── Demand calculation ──
    # Base demand fluctuation
    noise = random.gauss(0, MARKET["demand_volatility"] * 500)
    base_demand = MARKET["base_demand"] * demand_multiplier

    # Price elasticity effect
    price_ratio = market.price / MARKET["base_price"]
    price_effect = price_ratio ** MARKET["price_elasticity"]

    # Marketing boost
    marketing_boost = 1.0 + marketing_effectiveness * 0.3

    # Quality retention
    quality_factor = 0.7 + product_quality * 0.6

    market.demand = max(100, base_demand * price_effect * marketing_boost * quality_factor + noise)

    # ── Market share dynamics ──
    # Share grows with good satisfaction and marketing, decays with competition
    share_growth = (
        (market.customer_satisfaction - 0.5) * 0.005
        + marketing_effectiveness * 0.003
        - market.competition_level * 0.002
    )

    if expand_market:
        share_growth += 0.01  # Expansion action bonus
        changes.append("Market expansion in progress (+1% share boost)")

    market.market_share = max(0.01, min(0.60, market.market_share + share_growth))

    # ── Brand awareness ──
    awareness_growth = marketing_effectiveness * 0.005 - 0.001  # Slow decay without marketing
    market.brand_awareness = max(0.0, min(1.0, market.brand_awareness + awareness_growth))

    # ── Competition level fluctuation ──
    comp_change = random.gauss(0, 0.01)
    market.competition_level = max(0.1, min(0.9, market.competition_level + comp_change))

    # ── Customer satisfaction ──
    # Affected by product quality, pricing fairness, and brand
    sat_target = (
        product_quality * 0.4
        + (1.0 - price_ratio) * 0.2  # Lower price → higher satisfaction
        + market.brand_awareness * 0.2
        + 0.2  # Base
    )
    sat_target = max(0.1, min(1.0, sat_target))
    market.customer_satisfaction += (sat_target - market.customer_satisfaction) * 0.1

    changes.append(
        f"Demand: {market.demand:,.0f} | Share: {market.market_share:.1%} | "
        f"Satisfaction: {market.customer_satisfaction:.0%}"
    )

    return " | ".join(changes)


def calculate_daily_revenue(
    market: MarketState,
    employee_count: int,
    operations_effectiveness: float = 0.5,
) -> float:
    """
    Calculate daily revenue from market conditions and operational capacity.
    """
    # How many units you can sell is limited by capacity
    capacity = employee_count * 20 * operations_effectiveness  # Units per day
    potential_sales = market.demand * market.market_share
    actual_sales = min(capacity, potential_sales)

    revenue = actual_sales * market.price / 30  # Daily portion of monthly demand
    return max(0, revenue)


def get_market_summary(market: MarketState) -> str:
    """Generate a human-readable market summary."""
    return (
        f"Market: share={market.market_share:.1%}, demand={market.demand:,.0f}, "
        f"price=${market.price:.0f}, satisfaction={market.customer_satisfaction:.0%}, "
        f"brand={market.brand_awareness:.0%}, competition={market.competition_level:.0%}"
    )
