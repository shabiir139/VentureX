# ─── VentureX · Company Simulation ──────────────────────────────────────────
"""
Simulates a company's departments, P&L, and operations.
Each department's budget and effectiveness impact revenue, costs, and satisfaction.
"""
from __future__ import annotations
import random
from src.models import DepartmentState, FinancialState
from src.constants import DEPARTMENTS


def create_departments() -> dict[str, DepartmentState]:
    """Create initial department states with default budgets."""
    depts = {}
    for key, cfg in DEPARTMENTS.items():
        depts[key] = DepartmentState(
            name=cfg["metrics"][0].replace("_", " ").title() if cfg["metrics"] else key.title(),
            budget=cfg["default_budget"],
            effectiveness=0.5,
            headcount=2,
            metrics={m: 0.5 for m in cfg["metrics"]},
        )
        depts[key].name = key.replace("_", " ").title()
    return depts


def process_department_effects(
    departments: dict[str, DepartmentState],
    financials: FinancialState,
    employee_count: int,
) -> tuple[float, float, float]:
    """
    Process all departments and return (daily_revenue_boost, daily_cost, satisfaction_delta).
    """
    total_revenue_boost = 0.0
    total_cost = 0.0
    satisfaction_delta = 0.0

    for key, dept in departments.items():
        cfg = DEPARTMENTS.get(key, {})
        if not cfg:
            continue

        # Budget drives effectiveness (diminishing returns)
        budget_ratio = dept.budget / max(cfg["default_budget"], 1)
        effectiveness_target = min(0.95, 0.3 + 0.5 * (budget_ratio ** 0.6))
        dept.effectiveness += (effectiveness_target - dept.effectiveness) * 0.15

        # Revenue contribution from this department
        rev_impact = cfg.get("revenue_impact", 0.1)
        dept_rev = dept.effectiveness * rev_impact * dept.budget * 0.02
        total_revenue_boost += dept_rev

        # Cost is salary + operational
        salary_cost = dept.headcount * 200  # $200/day per employee
        operational_cost = dept.budget * 0.003  # 0.3% daily operational cost
        total_cost += salary_cost + operational_cost

        # Satisfaction impact
        sat_impact = cfg.get("satisfaction_impact", 0.1)
        satisfaction_delta += (dept.effectiveness - 0.5) * sat_impact * 0.02

        # Update department metrics
        noise = random.uniform(-0.02, 0.02)
        for m in dept.metrics:
            dept.metrics[m] = max(0.0, min(1.0,
                dept.metrics[m] + (dept.effectiveness - 0.5) * 0.05 + noise
            ))

    return total_revenue_boost, total_cost, satisfaction_delta


def apply_budget_allocation(
    departments: dict[str, DepartmentState],
    department: str,
    amount: float,
) -> str:
    """Allocate budget to a specific department."""
    if department not in departments:
        return f"Department '{department}' not found."

    dept = departments[department]
    old_budget = dept.budget
    dept.budget = max(0, amount)
    return (
        f"Budget for {department} changed from ${old_budget:,.0f} to ${dept.budget:,.0f}. "
        f"Effectiveness will adjust over time."
    )


def apply_hire(
    departments: dict[str, DepartmentState],
    department: str,
    count: int,
) -> tuple[str, int]:
    """Hire employees in a department. Returns (message, total_new_employees)."""
    if department not in departments:
        return f"Department '{department}' not found.", 0

    dept = departments[department]
    actual = max(1, min(count, 10))  # Cap at 10 hires per action
    dept.headcount += actual
    # Hiring temporarily dips effectiveness (onboarding)
    dept.effectiveness *= 0.95
    return (
        f"Hired {actual} people in {department}. "
        f"Headcount: {dept.headcount}. Effectiveness temporarily dipped due to onboarding.",
        actual,
    )


def calculate_pnl(financials: FinancialState) -> None:
    """Update P&L derived metrics."""
    financials.profit = financials.revenue - financials.expenses
    financials.burn_rate = max(0, financials.daily_expenses - financials.daily_revenue)
    if financials.burn_rate > 0:
        financials.runway_days = int(financials.cash / financials.burn_rate)
    else:
        financials.runway_days = 999
    if financials.revenue > 0:
        financials.profit_margin = financials.profit / financials.revenue
    else:
        financials.profit_margin = 0.0
