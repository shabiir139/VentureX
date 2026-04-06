# ─── VentureX · Task Configurations ────────────────────────────────────────
"""Task definitions with their specific configurations and graders."""
from __future__ import annotations
from src.models import TaskConfig


# ── Task 1: Grow a Startup ──
TASK_GROW_STARTUP = TaskConfig(
    task_name="grow_startup",
    max_days=90,
    description=(
        "You are the CEO of a brand-new startup. Your goal is to grow from the IDEA stage "
        "all the way to SCALE stage within 90 days. Make strategic decisions about hiring, "
        "budget allocation, product development, marketing, and fundraising. Each day you "
        "must choose one action to advance your company."
    ),
    initial_cash=500_000,
    initial_stage="IDEA",
    force_events=[],
    target={"stage": "SCALE", "min_revenue": 100_000},
)

# ── Task 2: Survive Economic Downturn ──
TASK_SURVIVE_DOWNTURN = TaskConfig(
    task_name="survive_downturn",
    max_days=60,
    description=(
        "Your startup is in the GROWTH stage when a severe economic downturn hits. "
        "Demand drops, costs rise, and investors pull back. Your goal is to survive 60 days "
        "with positive cash flow. You must cut costs wisely, preserve cash, maintain customer "
        "satisfaction, and pivot strategy if needed."
    ),
    initial_cash=300_000,
    initial_stage="GROWTH",
    force_events=["economic_downturn", "inflation_spike"],
    target={"survive_days": 60, "min_cash": 0},
)

# ── Task 3: Reach Profitability ──
TASK_REACH_PROFITABILITY = TaskConfig(
    task_name="reach_profitability",
    max_days=90,
    description=(
        "Your company has been operating for a while and has reached the MARKET_TEST stage. "
        "Investors are demanding profitability. Your goal is to reach $1M total revenue with "
        "a profit margin above 15% within 90 days. Balance growth investments with cost control."
    ),
    initial_cash=400_000,
    initial_stage="MARKET_TEST",
    force_events=[],
    target={"revenue": 1_000_000, "profit_margin": 0.15},
)

# ── Task 4: Market Expansion ──
TASK_MARKET_EXPANSION = TaskConfig(
    task_name="market_expansion",
    max_days=90,
    description=(
        "Your company has a solid product in the MVP stage with 5% market share. "
        "The board wants aggressive growth. Expand your market share to 25%+ within 90 days "
        "through marketing, pricing strategy, product improvement, and team scaling. "
        "Watch out for competitors and market disruptions."
    ),
    initial_cash=600_000,
    initial_stage="MVP",
    force_events=["new_competitor"],
    target={"market_share": 0.25},
)

# ── Registry ──
ALL_TASKS = {
    "grow_startup": TASK_GROW_STARTUP,
    "survive_downturn": TASK_SURVIVE_DOWNTURN,
    "reach_profitability": TASK_REACH_PROFITABILITY,
    "market_expansion": TASK_MARKET_EXPANSION,
}
