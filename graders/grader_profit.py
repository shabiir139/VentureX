# ─── VentureX · Grader — Reach Profitability ───────────────────────────────
"""Grades Task 3: Reach $1M revenue with >15% profit margin within 90 days."""
from graders import BaseGrader


class ProfitabilityGrader(BaseGrader):
    def __init__(self):
        super().__init__(
            task_name="reach_profitability",
            description="Reach $1M total revenue with >15% profit margin within 90 days",
        )

    def grade(self, final_score: dict) -> dict:
        revenue = final_score.get("total_revenue", 0)
        profit = final_score.get("total_profit", 0)
        margin = final_score.get("final_profit_margin", 0)
        cash = final_score.get("final_cash", 0)
        peak_rev = final_score.get("peak_daily_revenue", 0)
        days = final_score.get("days_survived", 0)

        target_revenue = 1_000_000
        target_margin = 0.15

        # Revenue achievement (35%)
        rev_score = min(1.0, revenue / target_revenue)

        # Profit margin (30%)
        if margin >= target_margin:
            margin_score = 1.0
        elif margin > 0:
            margin_score = margin / target_margin
        else:
            margin_score = 0.0

        # Total profit (15%)
        if profit > 0:
            profit_score = min(1.0, profit / 150_000)
        else:
            profit_score = 0.0

        # Revenue growth trajectory (10%)
        if days > 0:
            avg_rev = revenue / days
            growth_score = min(1.0, peak_rev / max(avg_rev * 2, 1))
        else:
            growth_score = 0.0

        # Cash position (10%)
        cash_score = min(1.0, max(0, cash) / 500_000)

        score = (
            0.35 * rev_score
            + 0.30 * margin_score
            + 0.15 * profit_score
            + 0.10 * growth_score
            + 0.10 * cash_score
        )

        return {
            "score": self._clamp(score),
            "breakdown": {
                "revenue_achievement": round(rev_score, 3),
                "profit_margin": round(margin_score, 3),
                "total_profit": round(profit_score, 3),
                "growth_trajectory": round(growth_score, 3),
                "cash_position": round(cash_score, 3),
            },
            "feedback": (
                f"Revenue: ${revenue:,.0f}/${target_revenue:,.0f} target. "
                f"Margin: {margin:.1%} (target: {target_margin:.0%}). "
                f"Total profit: ${profit:,.0f}. Peak daily: ${peak_rev:,.0f}."
            ),
        }
