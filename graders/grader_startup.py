# ─── VentureX · Grader — Grow Startup ──────────────────────────────────────
"""Grades Task 1: Grow a startup from IDEA to SCALE within 90 days."""
from graders import BaseGrader


class GrowStartupGrader(BaseGrader):
    def __init__(self):
        super().__init__(
            task_name="grow_startup",
            description="Grow a startup from IDEA stage to SCALE stage within 90 days",
        )

    def grade(self, final_score: dict) -> dict:
        stage_order = final_score.get("stage_order", 0)
        max_order = final_score.get("max_stage_order", 4)
        days = final_score.get("days_survived", 0)
        revenue = final_score.get("total_revenue", 0)
        cash = final_score.get("final_cash", 0)
        satisfaction = final_score.get("final_satisfaction", 0)
        funding = final_score.get("total_funding_raised", 0)

        # Stage progression is the primary metric (50%)
        stage_score = stage_order / max_order

        # Speed bonus — reaching SCALE faster is better (15%)
        if stage_order >= max_order:
            speed_score = max(0, 1.0 - (days - 30) / 60)  # Best if done by day 30
        else:
            speed_score = 0.2 * (stage_order / max_order)

        # Financial health (15%)
        cash_score = min(1.0, max(0, cash) / 500_000)

        # Revenue traction (10%)
        rev_score = min(1.0, revenue / 200_000)

        # Customer satisfaction (10%)
        sat_score = satisfaction

        score = (
            0.50 * stage_score
            + 0.15 * speed_score
            + 0.15 * cash_score
            + 0.10 * rev_score
            + 0.10 * sat_score
        )

        return {
            "score": self._clamp(score),
            "breakdown": {
                "stage_progression": round(stage_score, 3),
                "speed": round(speed_score, 3),
                "financial_health": round(cash_score, 3),
                "revenue_traction": round(rev_score, 3),
                "satisfaction": round(sat_score, 3),
            },
            "feedback": (
                f"Reached stage {final_score.get('stage_reached', '?')} "
                f"({stage_order}/{max_order}) in {days} days. "
                f"Revenue: ${revenue:,.0f}, Cash: ${cash:,.0f}, "
                f"Satisfaction: {satisfaction:.0%}."
            ),
        }
