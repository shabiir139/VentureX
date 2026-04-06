# ─── VentureX · Core Environment ────────────────────────────────────────────
"""
The main OpenEnv-compliant simulation environment.
Orchestrates all modules and exposes reset(), step(), state() interface.
"""
from __future__ import annotations
import random

from src.models import (
    Action, Observation, StepResult, TaskConfig,
    FinancialState, MarketState, DepartmentState, ActiveEvent, DailyLogEntry,
)
from src.constants import (
    MAX_DAYS, STARTING_CASH, STARTING_MARKET_SHARE, STARTING_EMPLOYEES,
    STARTING_SATISFACTION, ACTION_TYPES, STAGE_ORDER, STAGES,
    SCORING_WEIGHTS,
)
from src.company import (
    create_departments, process_department_effects,
    apply_budget_allocation, apply_hire, calculate_pnl,
)
from src.startup import (
    check_stage_progression, advance_stage,
    process_funding_round, process_pivot,
)
from src.economy import update_market, calculate_daily_revenue, get_market_summary
from src.scenarios import roll_for_events, get_combined_multipliers, get_events_summary
from src.timeline import Timeline


class VentureXEnv:
    """
    OpenEnv-compliant business simulation environment.

    The agent plays as a startup CEO making daily decisions.
    Each step() advances one simulated day.
    """

    def __init__(self, task_config: TaskConfig | None = None):
        self.task_config = task_config
        self.max_days = task_config.max_days if task_config else MAX_DAYS
        self._reset_state()

    def _reset_state(self):
        """Initialize all internal state."""
        tc = self.task_config

        self.day = 0
        self.stage = tc.initial_stage if tc else "IDEA"
        self.days_in_stage = 0
        self.terminated = False
        self.truncated = False

        # Financials
        self.financials = FinancialState(
            cash=tc.initial_cash if tc else STARTING_CASH,
        )

        # Market
        self.market = MarketState(
            market_share=STARTING_MARKET_SHARE,
            customer_satisfaction=STARTING_SATISFACTION,
        )

        # Departments
        self.departments = create_departments()

        # Team
        self.employee_count = STARTING_EMPLOYEES
        self.employee_morale = 0.7

        # Events
        self.active_events: list[ActiveEvent] = []
        self.forced_events = list(tc.force_events) if tc and tc.force_events else []

        # Timeline
        self.timeline = Timeline()

        # Track cumulative metrics for scoring
        self._peak_revenue = 0.0
        self._total_revenue = 0.0
        self._total_profit = 0.0
        self._days_profitable = 0
        self._stage_history: list[str] = [self.stage]

    def reset(self) -> Observation:
        """Reset the environment and return initial observation."""
        self._reset_state()
        self.day = 1
        return self._build_observation()

    def state(self) -> Observation:
        """Return current observation without advancing."""
        return self._build_observation()

    def step(self, action: Action) -> StepResult:
        """
        Execute one business decision and advance one day.
        Returns StepResult with observation, reward, terminated, truncated, info.
        """
        if self.terminated or self.truncated:
            return StepResult(
                observation=self._build_observation(),
                reward=0.0,
                terminated=self.terminated,
                truncated=self.truncated,
                info={"message": "Episode already ended."},
            )

        # ── 1. Process the action ──
        outcome, rev_change, cash_change = self._process_action(action)

        # ── 2. Get scenario multipliers ──
        multipliers = get_combined_multipliers(self.active_events)

        # ── 3. Process department effects ──
        dept_rev, dept_cost, sat_delta = process_department_effects(
            self.departments, self.financials, self.employee_count
        )

        # ── 4. Update market ──
        price_change = 0.0
        expand = False
        if action.action_type == "set_price":
            price_change = action.parameters.get("amount", 0.0) - self.market.price
        if action.action_type == "expand_market":
            expand = True

        mkt_eff = self.departments.get("marketing", DepartmentState(name="m")).effectiveness
        prod_eff = self.departments.get("product", DepartmentState(name="p")).effectiveness

        market_summary = update_market(
            self.market, self.day,
            marketing_effectiveness=mkt_eff,
            product_quality=prod_eff,
            price_change=price_change,
            expand_market=expand,
            demand_multiplier=multipliers["demand"],
        )

        # ── 5. Calculate daily revenue & expenses ──
        ops_eff = self.departments.get("operations", DepartmentState(name="o")).effectiveness
        daily_rev = calculate_daily_revenue(self.market, self.employee_count, ops_eff)
        daily_rev += dept_rev
        daily_rev *= multipliers["demand"]  # Events affect revenue

        daily_exp = dept_cost * multipliers["cost"]
        daily_exp += self.employee_count * 150  # Base salary cost

        # Apply to financials
        self.financials.daily_revenue = daily_rev
        self.financials.daily_expenses = daily_exp
        self.financials.revenue += daily_rev
        self.financials.expenses += daily_exp
        self.financials.cash += daily_rev - daily_exp + cash_change
        calculate_pnl(self.financials)

        # Track metrics
        self._peak_revenue = max(self._peak_revenue, daily_rev)
        self._total_revenue += daily_rev
        self._total_profit += daily_rev - daily_exp
        if daily_rev > daily_exp:
            self._days_profitable += 1

        # ── 6. Update satisfaction ──
        self.market.customer_satisfaction = max(0.05, min(1.0,
            self.market.customer_satisfaction + sat_delta
        ))

        # ── 7. Roll for events ──
        self.active_events = roll_for_events(self.day, self.active_events, self.forced_events)

        # ── 8. Check stage progression ──
        can_advance, stage_reason = check_stage_progression(
            self.stage, self.days_in_stage,
            self.financials.cash, self.financials.revenue,
            self.market.market_share, self.market.customer_satisfaction,
        )
        stage_msg = ""
        if can_advance:
            self.stage, stage_label = advance_stage(self.stage)
            self.days_in_stage = 0
            self._stage_history.append(self.stage)
            stage_msg = f"🚀 Advanced to {stage_label}! {stage_reason}"
        else:
            self.days_in_stage += 1

        # ── 9. Log to timeline ──
        self.timeline.log_action(
            day=self.day,
            action_taken=action.action_type,
            department=action.department,
            outcome=outcome + (f" | {stage_msg}" if stage_msg else ""),
            revenue_change=daily_rev,
            cash_change=cash_change,
        )

        events_summary = get_events_summary(self.active_events)
        self.timeline.generate_daily_summary(
            self.day, self.stage, self.financials.cash,
            self.financials.revenue, self.market.market_share,
            self.market.customer_satisfaction, events_summary,
        )

        # ── 10. Check termination ──
        info = {
            "action_outcome": outcome,
            "market_update": market_summary,
            "stage_message": stage_msg,
            "events": events_summary,
        }

        if self.financials.cash <= 0:
            self.terminated = True
            info["termination_reason"] = "Ran out of cash — game over!"
        elif self.day >= self.max_days:
            self.truncated = True
            info["truncation_reason"] = f"Reached maximum day limit ({self.max_days})"

        # ── 11. Calculate reward ──
        reward = self._calculate_reward()

        # ── 12. Advance day ──
        self.day += 1

        return StepResult(
            observation=self._build_observation(),
            reward=reward,
            terminated=self.terminated,
            truncated=self.truncated,
            info=info,
        )

    def _process_action(self, action: Action) -> tuple[str, float, float]:
        """
        Process a single action. Returns (outcome_text, revenue_change, cash_change).
        """
        params = action.parameters
        rev_change = 0.0
        cash_change = 0.0

        if action.action_type == "allocate_budget":
            amount = params.get("amount", 50_000)
            outcome = apply_budget_allocation(self.departments, action.department, amount)

        elif action.action_type == "hire":
            count = params.get("count", 1)
            outcome, hired = apply_hire(self.departments, action.department, count)
            self.employee_count += hired
            # Hiring cost
            cash_change -= hired * 5000  # $5k hiring cost per person

        elif action.action_type == "set_price":
            new_price = params.get("amount", self.market.price)
            old = self.market.price
            outcome = f"Price adjusted: ${old:.0f} → ${new_price:.0f}"

        elif action.action_type == "launch_product":
            cost = params.get("cost", 50_000)
            cash_change -= cost
            quality = random.uniform(0.4, 0.9)
            self.market.customer_satisfaction += quality * 0.05
            self.market.brand_awareness += 0.05
            outcome = f"Product launched! Investment: ${cost:,.0f}. Quality: {quality:.0%}"

        elif action.action_type == "raise_funding":
            multipliers = get_combined_multipliers(self.active_events)
            amount, outcome = process_funding_round(
                self.stage, self.financials.cash, self.financials.total_funding_raised,
                self.market.market_share, self.financials.revenue,
                multipliers["funding"],
            )
            cash_change += amount
            self.financials.total_funding_raised += amount

        elif action.action_type == "pivot":
            new_share, new_sat, outcome = process_pivot(
                self.stage, self.market.market_share, self.market.customer_satisfaction,
            )
            self.market.market_share = new_share
            self.market.customer_satisfaction = new_sat

        elif action.action_type == "expand_market":
            cost = params.get("cost", 30_000)
            cash_change -= cost
            outcome = f"Market expansion initiated. Investment: ${cost:,.0f}"

        elif action.action_type == "cut_costs":
            pct = params.get("percentage", 10) / 100
            for dept in self.departments.values():
                dept.budget *= (1 - pct)
                dept.effectiveness *= 0.95  # Cutting costs hurts effectiveness
            outcome = f"Cut costs by {pct:.0%} across departments"

        elif action.action_type == "invest_rd":
            amount = params.get("amount", 30_000)
            cash_change -= amount
            prod_dept = self.departments.get("product")
            if prod_dept:
                prod_dept.effectiveness = min(0.95, prod_dept.effectiveness + 0.05)
            outcome = f"R&D investment: ${amount:,.0f}. Product quality improving."

        elif action.action_type == "run_marketing_campaign":
            budget = params.get("budget", 20_000)
            cash_change -= budget
            mkt_dept = self.departments.get("marketing")
            if mkt_dept:
                mkt_dept.effectiveness = min(0.95, mkt_dept.effectiveness + 0.03)
            self.market.brand_awareness = min(1.0, self.market.brand_awareness + 0.03)
            outcome = f"Marketing campaign launched! Budget: ${budget:,.0f}"

        else:
            outcome = f"Unknown action: {action.action_type}. No effect."

        return outcome, rev_change, cash_change

    def _calculate_reward(self) -> float:
        """
        Calculate reward as a float between 0.0 and 1.0.
        Based on multiple business health indicators.
        """
        # Revenue score (normalized to target of $10k/day)
        rev_score = min(1.0, self.financials.daily_revenue / 10_000)

        # Profitability score
        if self.financials.daily_revenue > 0:
            profit_score = max(0, min(1.0, self.financials.profit_margin + 0.5))
        else:
            profit_score = 0.0

        # Market share score (target 25%)
        share_score = min(1.0, self.market.market_share / 0.25)

        # Satisfaction score
        sat_score = self.market.customer_satisfaction

        # Sustainability (cash runway)
        sustain_score = min(1.0, self.financials.runway_days / 90)

        # Weighted composite
        reward = (
            SCORING_WEIGHTS["revenue"] * rev_score
            + SCORING_WEIGHTS["profitability"] * profit_score
            + SCORING_WEIGHTS["market_share"] * share_score
            + SCORING_WEIGHTS["customer_satisfaction"] * sat_score
            + SCORING_WEIGHTS["sustainability"] * sustain_score
        )

        return round(max(0.0, min(1.0, reward)), 4)

    def _build_observation(self) -> Observation:
        """Build the current observation for the agent."""
        events_summary = get_events_summary(self.active_events)
        market_summary = get_market_summary(self.market)

        status = (
            f"Day {self.day}/{self.max_days} | Stage: {STAGES.get(self.stage, {}).get('label', self.stage)} | "
            f"Cash: ${self.financials.cash:,.0f} | "
            f"Daily Rev: ${self.financials.daily_revenue:,.0f} | "
            f"Burn: ${self.financials.burn_rate:,.0f}/day | "
            f"Runway: {self.financials.runway_days}d\n"
            f"{market_summary}\n"
            f"{events_summary}"
        )

        return Observation(
            day=self.day,
            max_days=self.max_days,
            stage=self.stage,
            stage_label=STAGES.get(self.stage, {}).get("label", self.stage),
            days_in_stage=self.days_in_stage,
            financials=self.financials.model_copy(),
            market=self.market.model_copy(),
            departments={k: v.model_copy() for k, v in self.departments.items()},
            employee_count=self.employee_count,
            employee_morale=self.employee_morale,
            active_events=[e.model_copy() for e in self.active_events],
            available_actions=ACTION_TYPES,
            daily_log=self.timeline.get_recent_entries(5),
            status_summary=status,
        )

    def get_final_score(self) -> dict:
        """Get final scoring breakdown for grading."""
        return {
            "stage_reached": self.stage,
            "stage_order": STAGE_ORDER.index(self.stage) if self.stage in STAGE_ORDER else 0,
            "max_stage_order": len(STAGE_ORDER) - 1,
            "total_revenue": self._total_revenue,
            "total_profit": self._total_profit,
            "peak_daily_revenue": self._peak_revenue,
            "days_profitable": self._days_profitable,
            "final_cash": self.financials.cash,
            "final_market_share": self.market.market_share,
            "final_satisfaction": self.market.customer_satisfaction,
            "final_profit_margin": self.financials.profit_margin,
            "employee_count": self.employee_count,
            "total_funding_raised": self.financials.total_funding_raised,
            "stages_visited": self._stage_history,
            "days_survived": self.day - 1,
            "timeline_stats": self.timeline.get_stats(),
        }
