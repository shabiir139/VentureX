# ─── VentureX · Day-by-Day Timeline ─────────────────────────────────────────
"""
Tracks the day-by-day progression of the simulation.
Logs completed tasks per day, creates daily summaries, and maintains history.
"""
from __future__ import annotations
from src.models import DailyLogEntry


class Timeline:
    """Manages the day-by-day timeline and daily task log."""

    def __init__(self):
        self.entries: list[DailyLogEntry] = []
        self.daily_summaries: dict[int, str] = {}

    def log_action(
        self,
        day: int,
        action_taken: str,
        department: str,
        outcome: str,
        revenue_change: float = 0.0,
        cash_change: float = 0.0,
        key_metrics: dict[str, float] | None = None,
    ) -> DailyLogEntry:
        """Log an action taken on a specific day."""
        entry = DailyLogEntry(
            day=day,
            action_taken=action_taken,
            department=department,
            outcome=outcome,
            revenue_change=revenue_change,
            cash_change=cash_change,
            key_metrics=key_metrics or {},
        )
        self.entries.append(entry)
        return entry

    def get_day_entries(self, day: int) -> list[DailyLogEntry]:
        """Get all log entries for a specific day."""
        return [e for e in self.entries if e.day == day]

    def get_recent_entries(self, count: int = 5) -> list[DailyLogEntry]:
        """Get the most recent N log entries."""
        return self.entries[-count:] if self.entries else []

    def generate_daily_summary(
        self,
        day: int,
        stage: str,
        cash: float,
        revenue: float,
        market_share: float,
        satisfaction: float,
        events_summary: str,
    ) -> str:
        """Generate a human-readable summary for the day."""
        day_entries = self.get_day_entries(day)
        actions_text = ""
        if day_entries:
            actions_text = "\n".join(
                f"  • {e.action_taken} ({e.department}): {e.outcome}"
                for e in day_entries
            )
        else:
            actions_text = "  • No actions taken"

        summary = (
            f"═══ DAY {day} REPORT ═══\n"
            f"Stage: {stage}\n"
            f"Cash: ${cash:,.0f} | Revenue: ${revenue:,.0f} | "
            f"Market Share: {market_share:.1%} | Satisfaction: {satisfaction:.0%}\n"
            f"\nActions Completed:\n{actions_text}\n"
            f"\nMarket Events:\n  {events_summary}\n"
            f"{'═' * 40}"
        )
        self.daily_summaries[day] = summary
        return summary

    def get_timeline_report(self) -> str:
        """Get full timeline report of all days."""
        if not self.daily_summaries:
            return "No days completed yet."
        lines = []
        for day in sorted(self.daily_summaries.keys()):
            lines.append(self.daily_summaries[day])
        return "\n\n".join(lines)

    def get_stats(self) -> dict:
        """Get aggregate timeline statistics."""
        if not self.entries:
            return {"total_actions": 0, "days_active": 0}

        days = set(e.day for e in self.entries)
        total_rev_change = sum(e.revenue_change for e in self.entries)
        total_cash_change = sum(e.cash_change for e in self.entries)

        return {
            "total_actions": len(self.entries),
            "days_active": len(days),
            "total_revenue_impact": total_rev_change,
            "total_cash_impact": total_cash_change,
        }
