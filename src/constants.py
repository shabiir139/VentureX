# ─── VentureX · Game Constants ──────────────────────────────────────────────

# ── Simulation Timeline ─────────────────────────────
MAX_DAYS = 90                    # Default episode length
STARTING_CASH = 500_000         # $500k starting capital
STARTING_MARKET_SHARE = 0.05    # 5% initial share
STARTING_EMPLOYEES = 5          # Founding team
STARTING_SATISFACTION = 0.7     # 70% customer satisfaction

# ── Startup Stages ──────────────────────────────────
STAGES = {
    "IDEA":        {"order": 0, "label": "Ideation",        "min_days": 1,  "max_days": 5,  "funding_unlock": 0},
    "MVP":         {"order": 1, "label": "MVP Development", "min_days": 3,  "max_days": 10, "funding_unlock": 50_000},
    "MARKET_TEST": {"order": 2, "label": "Market Testing",  "min_days": 5,  "max_days": 14, "funding_unlock": 200_000},
    "GROWTH":      {"order": 3, "label": "Growth Phase",    "min_days": 7,  "max_days": 21, "funding_unlock": 500_000},
    "SCALE":       {"order": 4, "label": "Scaling",         "min_days": 10, "max_days": 30, "funding_unlock": 2_000_000},
}

STAGE_ORDER = ["IDEA", "MVP", "MARKET_TEST", "GROWTH", "SCALE"]

# ── Department Defaults ─────────────────────────────
DEPARTMENTS = {
    "marketing": {
        "default_budget": 50_000,
        "revenue_impact": 0.30,
        "satisfaction_impact": 0.20,
        "metrics": ["brand_awareness", "cac", "ad_roi"],
    },
    "finance": {
        "default_budget": 30_000,
        "revenue_impact": 0.05,
        "satisfaction_impact": 0.05,
        "metrics": ["cash_flow", "debt_ratio", "roi"],
    },
    "operations": {
        "default_budget": 80_000,
        "revenue_impact": 0.25,
        "satisfaction_impact": 0.30,
        "metrics": ["production_efficiency", "supply_chain", "quality"],
    },
    "hr": {
        "default_budget": 40_000,
        "revenue_impact": 0.10,
        "satisfaction_impact": 0.15,
        "metrics": ["employee_satisfaction", "productivity", "turnover"],
    },
    "product": {
        "default_budget": 60_000,
        "revenue_impact": 0.20,
        "satisfaction_impact": 0.25,
        "metrics": ["feature_velocity", "bug_rate", "user_adoption"],
    },
}

# ── Market / Economy ────────────────────────────────
MARKET = {
    "base_demand": 10_000,
    "price_elasticity": -1.2,
    "inflation_rate": 0.02,
    "competition_intensity": 0.5,
    "demand_volatility": 0.15,
    "base_price": 100.0,
}

# ── Scenario Events ─────────────────────────────────
SCENARIO_EVENTS = [
    {
        "id": "economic_downturn",
        "name": "Economic Downturn",
        "description": "The economy enters a recession. Demand drops 30% and investors pull back.",
        "demand_multiplier": 0.7,
        "cost_multiplier": 1.1,
        "funding_multiplier": 0.5,
        "duration_days": 14,
        "probability": 0.03,
    },
    {
        "id": "inflation_spike",
        "name": "Inflation Spike",
        "description": "Sudden inflation increases all operational costs by 25%.",
        "demand_multiplier": 0.9,
        "cost_multiplier": 1.25,
        "funding_multiplier": 0.8,
        "duration_days": 10,
        "probability": 0.04,
    },
    {
        "id": "new_competitor",
        "name": "New Competitor Enters Market",
        "description": "A well-funded competitor launches a similar product at lower prices.",
        "demand_multiplier": 0.8,
        "cost_multiplier": 1.0,
        "funding_multiplier": 1.0,
        "duration_days": 21,
        "probability": 0.05,
    },
    {
        "id": "supply_chain_disruption",
        "name": "Supply Chain Disruption",
        "description": "Global supply chain issues increase delivery times and costs.",
        "demand_multiplier": 0.85,
        "cost_multiplier": 1.35,
        "funding_multiplier": 0.9,
        "duration_days": 12,
        "probability": 0.04,
    },
    {
        "id": "tech_breakthrough",
        "name": "Technology Breakthrough",
        "description": "A new technology emerges that can boost your product capabilities.",
        "demand_multiplier": 1.2,
        "cost_multiplier": 0.9,
        "funding_multiplier": 1.3,
        "duration_days": 14,
        "probability": 0.03,
    },
    {
        "id": "viral_marketing",
        "name": "Viral Marketing Moment",
        "description": "Your product goes viral on social media! Demand surges temporarily.",
        "demand_multiplier": 1.5,
        "cost_multiplier": 1.0,
        "funding_multiplier": 1.2,
        "duration_days": 7,
        "probability": 0.02,
    },
    {
        "id": "key_employee_exit",
        "name": "Key Employee Exits",
        "description": "A crucial team member leaves, impacting productivity and morale.",
        "demand_multiplier": 1.0,
        "cost_multiplier": 1.15,
        "funding_multiplier": 0.9,
        "duration_days": 10,
        "probability": 0.05,
    },
    {
        "id": "regulation_change",
        "name": "Regulatory Change",
        "description": "New regulations require compliance costs and process changes.",
        "demand_multiplier": 0.95,
        "cost_multiplier": 1.20,
        "funding_multiplier": 0.85,
        "duration_days": 18,
        "probability": 0.03,
    },
    {
        "id": "investor_interest",
        "name": "Investor Interest Surge",
        "description": "Your sector is hot! Investors are eager to fund companies like yours.",
        "demand_multiplier": 1.05,
        "cost_multiplier": 1.0,
        "funding_multiplier": 1.5,
        "duration_days": 14,
        "probability": 0.03,
    },
    {
        "id": "market_expansion_opportunity",
        "name": "Market Expansion Opportunity",
        "description": "A new geographic market opens up with high demand for your product.",
        "demand_multiplier": 1.3,
        "cost_multiplier": 1.1,
        "funding_multiplier": 1.1,
        "duration_days": 21,
        "probability": 0.03,
    },
]

# ── Action Types ────────────────────────────────────
ACTION_TYPES = [
    "allocate_budget",
    "hire",
    "set_price",
    "launch_product",
    "raise_funding",
    "pivot",
    "expand_market",
    "cut_costs",
    "invest_rd",
    "run_marketing_campaign",
]

# ── Scoring ─────────────────────────────────────────
SCORING_WEIGHTS = {
    "revenue": 0.25,
    "profitability": 0.25,
    "market_share": 0.20,
    "customer_satisfaction": 0.15,
    "sustainability": 0.15,
}
