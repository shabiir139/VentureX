# ─── VentureX · Grader — Survive Downturn ──────────────────────────────────
"""Grades Task 2: Survive an economic downturn — maintain positive cash for 60 days."""
from graders import BaseGrader


class SurviveDownturnGrader(BaseGrader):
    def __init__(self):
        super().__init__(
            task_name="survive_downturn",
            description="Survive an economic downturn — maintain positive cash flow for 60 days",
        )

    def grade(self, final_score: dict) -> dict:
        days = final_score.get("days_survived", 0)
        max_days = 60
        cash = final_score.get("final_cash", 0)
        initial_cash = 500_000
        days_profitable = final_score.get("days_profitable", 0)
        market_share = final_score.get("final_market_share", 0)
        satisfaction = final_score.get("final_satisfaction", 0)

        # Survival is the primary metric (40%)
        survival_score = min(1.0, days / max_days)

        # Cash preservation (25%)
        if cash > 0:
            cash_score = min(1.0, cash / initial_cash)
        else:
            cash_score = 0.0

        # Profitability during downturn (15%)
        profit_ratio = days_profitable / max(days, 1)
        profit_score = profit_ratio

        # Market share maintenance (10%)
        share_score = min(1.0, market_share / 0.10)  # Maintaining 10% during downturn is great

        # Customer retention (10%)
        sat_score = satisfaction

        score = (
            0.40 * survival_score
            + 0.25 * cash_score
            + 0.15 * profit_score
            + 0.10 * share_score
            + 0.10 * sat_score
        )

        return {
            "score": self._clamp(score),
            "breakdown": {
                "survival": round(survival_score, 3),
                "cash_preservation": round(cash_score, 3),
                "profitability": round(profit_score, 3),
                "market_share": round(share_score, 3),
                "satisfaction": round(sat_score, 3),
            },
            "feedback": (
                f"Survived {days}/{max_days} days. "
                f"Cash: ${cash:,.0f} (started ${initial_cash:,.0f}). "
                f"Profitable {days_profitable}/{days} days. "
                f"Market share: {market_share:.1%}."
            ),
        }
