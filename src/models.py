# ─── VentureX · Pydantic Typed Models ──────────────────────────────────────
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Any


# ═══════════════════════════════════════════════════════════════════════════
#  ACTION — what the agent sends
# ═══════════════════════════════════════════════════════════════════════════
class Action(BaseModel):
    """A business decision made by the agent."""
    action_type: str = Field(
        ...,
        description="Type of action",
        examples=["allocate_budget", "hire", "set_price", "launch_product",
                   "raise_funding", "pivot", "expand_market", "cut_costs",
                   "invest_rd", "run_marketing_campaign"],
    )
    department: str = Field(
        default="executive",
        description="Target department",
        examples=["marketing", "finance", "operations", "hr", "product", "executive"],
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific parameters (amount, target, strategy, etc.)",
    )
    reasoning: str = Field(
        default="",
        description="Agent's reasoning for this decision",
    )


# ═══════════════════════════════════════════════════════════════════════════
#  DEPARTMENT STATE
# ═══════════════════════════════════════════════════════════════════════════
class DepartmentState(BaseModel):
    name: str
    budget: float = 0.0
    effectiveness: float = 0.5     # 0.0 – 1.0
    headcount: int = 1
    metrics: dict[str, float] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
#  FINANCIAL STATE
# ═══════════════════════════════════════════════════════════════════════════
class FinancialState(BaseModel):
    cash: float = 500_000.0
    revenue: float = 0.0
    daily_revenue: float = 0.0
    expenses: float = 0.0
    daily_expenses: float = 0.0
    profit: float = 0.0
    burn_rate: float = 0.0
    runway_days: int = 999
    total_funding_raised: float = 0.0
    debt: float = 0.0
    profit_margin: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════
#  MARKET STATE
# ═══════════════════════════════════════════════════════════════════════════
class MarketState(BaseModel):
    market_share: float = 0.05
    demand: float = 10_000.0
    price: float = 100.0
    competition_level: float = 0.5
    customer_satisfaction: float = 0.7
    brand_awareness: float = 0.1


# ═══════════════════════════════════════════════════════════════════════════
#  ACTIVE EVENT
# ═══════════════════════════════════════════════════════════════════════════
class ActiveEvent(BaseModel):
    id: str
    name: str
    description: str
    days_remaining: int
    demand_multiplier: float = 1.0
    cost_multiplier: float = 1.0
    funding_multiplier: float = 1.0


# ═══════════════════════════════════════════════════════════════════════════
#  DAILY LOG ENTRY
# ═══════════════════════════════════════════════════════════════════════════
class DailyLogEntry(BaseModel):
    day: int
    action_taken: str
    department: str
    outcome: str
    revenue_change: float = 0.0
    cash_change: float = 0.0
    key_metrics: dict[str, float] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
#  OBSERVATION — what the agent receives
# ═══════════════════════════════════════════════════════════════════════════
class Observation(BaseModel):
    """Full simulation state visible to the agent."""
    day: int = 1
    max_days: int = 90
    stage: str = "IDEA"
    stage_label: str = "Ideation"
    days_in_stage: int = 0

    # Financials
    financials: FinancialState = Field(default_factory=FinancialState)

    # Market
    market: MarketState = Field(default_factory=MarketState)

    # Departments
    departments: dict[str, DepartmentState] = Field(default_factory=dict)

    # Team
    employee_count: int = 5
    employee_morale: float = 0.7

    # Events
    active_events: list[ActiveEvent] = Field(default_factory=list)

    # Available decisions
    available_actions: list[str] = Field(default_factory=list)

    # Day-by-day log (last 5 days)
    daily_log: list[DailyLogEntry] = Field(default_factory=list)

    # Summary text for the agent
    status_summary: str = ""


# ═══════════════════════════════════════════════════════════════════════════
#  STEP RESULT — returned after each step()
# ═══════════════════════════════════════════════════════════════════════════
class StepResult(BaseModel):
    """Result of a step in the simulation."""
    observation: Observation
    reward: float = Field(0.0, ge=0.0, le=1.0)
    terminated: bool = False
    truncated: bool = False
    info: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
#  TASK CONFIG — configures a graded task
# ═══════════════════════════════════════════════════════════════════════════
class TaskConfig(BaseModel):
    task_name: str
    max_days: int = 90
    description: str = ""
    initial_cash: float = 500_000.0
    initial_stage: str = "IDEA"
    force_events: list[str] = Field(default_factory=list)
    target: dict[str, Any] = Field(default_factory=dict)
