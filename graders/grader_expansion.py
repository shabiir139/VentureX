# ─── VentureX · Grader — Market Expansion ──────────────────────────────────
"""Grades Task 4: Expand market share from 5% to 25%+ within 90 days."""
from graders import BaseGrader


class MarketExpansionGrader(BaseGrader):
    def __init__(self):
        super().__init__(
            task_name="market_expansion",
            description="Expand market share from 5% to 25%+ within 90 days",
        )

    def grade(self, final_score: dict) -> dict:
        market_share = final_score.get("final_market_share", 0.05)
        satisfaction = final_score.get("final_satisfaction", 0)
        revenue = final_score.get("total_revenue", 0)
        cash = final_score.get("final_cash", 0)
        employees = final_score.get("employee_count", 5)
        days = final_score.get("days_survived", 0)

        initial_share = 0.05
        target_share = 0.25

        # Market share achievement (40%)
        share_growth = market_share - initial_share
        target_growth = target_share - initial_share
        share_score = min(1.0, max(0, share_growth / target_growth))

        # Customer satisfaction during growth (20%)
        sat_score = satisfaction

        # Revenue supporting growth (15%)
        rev_score = min(1.0, revenue / 300_000)

        # Sustainable growth — cash remaining (15%)
        cash_score = min(1.0, max(0, cash) / 300_000)

        # Team scaling (10%)
        team_score = min(1.0, employees / 30)

        score = (
            0.40 * share_score
            + 0.20 * sat_score
            + 0.15 * rev_score
            + 0.15 * cash_score
            + 0.10 * team_score
        )

        return {
            "score": self._clamp(score),
            "breakdown": {
                "share_growth": round(share_score, 3),
                "satisfaction": round(sat_score, 3),
                "revenue": round(rev_score, 3),
                "cash_sustainability": round(cash_score, 3),
                "team_scaling": round(team_score, 3),
            },
            "feedback": (
                f"Market share: {initial_share:.0%} → {market_share:.1%} "
                f"(target: {target_share:.0%}). "
                f"Satisfaction: {satisfaction:.0%}. Revenue: ${revenue:,.0f}. "
                f"Team: {employees} employees."
            ),
        }
