# ─── VentureX · Scenario Engine ─────────────────────────────────────────────
"""
Generates and manages dynamic events (economic downturns, competitors, etc.)
that force adaptive decision-making.
"""
from __future__ import annotations
import random
from src.models import ActiveEvent
from src.constants import SCENARIO_EVENTS


def roll_for_events(
    day: int,
    active_events: list[ActiveEvent],
    forced_events: list[str] | None = None,
) -> list[ActiveEvent]:
    """
    Roll for new random events based on probability.
    Also tick down existing events.
    Returns updated list of active events.
    """
    new_events = []

    # Tick down existing events
    for event in active_events:
        event.days_remaining -= 1
        if event.days_remaining > 0:
            new_events.append(event)

    # Roll for new events (max 2 concurrent events)
    if len(new_events) < 2:
        for event_def in SCENARIO_EVENTS:
            # Check forced events first
            if forced_events and event_def["id"] in forced_events:
                # Force this event on specific days
                if day == 10:  # Trigger forced events on day 10
                    new_events.append(_create_event(event_def))
                    forced_events.remove(event_def["id"])
                continue

            # Random probability check
            if random.random() < event_def["probability"]:
                # Don't duplicate active events
                active_ids = {e.id for e in new_events}
                if event_def["id"] not in active_ids:
                    new_events.append(_create_event(event_def))
                    if len(new_events) >= 2:
                        break

    return new_events


def _create_event(event_def: dict) -> ActiveEvent:
    """Create an ActiveEvent from an event definition."""
    return ActiveEvent(
        id=event_def["id"],
        name=event_def["name"],
        description=event_def["description"],
        days_remaining=event_def["duration_days"],
        demand_multiplier=event_def["demand_multiplier"],
        cost_multiplier=event_def["cost_multiplier"],
        funding_multiplier=event_def["funding_multiplier"],
    )


def get_combined_multipliers(active_events: list[ActiveEvent]) -> dict[str, float]:
    """
    Combine multipliers from all active events.
    Multiple events stack multiplicatively.
    """
    demand_mul = 1.0
    cost_mul = 1.0
    funding_mul = 1.0

    for event in active_events:
        demand_mul *= event.demand_multiplier
        cost_mul *= event.cost_multiplier
        funding_mul *= event.funding_multiplier

    return {
        "demand": demand_mul,
        "cost": cost_mul,
        "funding": funding_mul,
    }


def get_events_summary(active_events: list[ActiveEvent]) -> str:
    """Generate a summary of all active events."""
    if not active_events:
        return "No active events."
    lines = []
    for e in active_events:
        lines.append(f"⚡ {e.name} ({e.days_remaining}d remaining): {e.description}")
    return "\n".join(lines)
