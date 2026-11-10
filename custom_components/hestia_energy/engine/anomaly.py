"""The unusual day (5.1): yesterday against what the home usually uses on such a day.

« Usually » is, when the heating is estimated from the cold, the home's own line for that day's cold (the summer rest
plus what the cold adds); else the same weekday of the four weeks before. A day is unusual only when it differs by at
least 40 % and 5 kWh: on Frank's real year, about one day a month above, six days a year below (absences).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import statistics

from .heating import Learned
from .rows import NAN, Rows

SHARE = 0.4      # the difference, as a share of the usual day
MIN_KWH = 5.0    # and at least this much, so a small home is not flagged for 2 kWh


@dataclass(frozen=True)
class Unusual:
    more: bool              # above the usual (watch) or below (an absence, learnt)
    used_kwh: float
    usual_kwh: float
    with_cold: bool         # the usual day takes that day's cold into account

    @property
    def gap_kwh(self) -> float:
        return abs(self.used_kwh - self.usual_kwh)


def usual(day: date, used: dict[date, float], learned: Learned | None, cold: dict[date, float]) -> tuple[float, bool] | None:
    """What the home usually uses on `day`, and whether the cold was taken into account. None when not known."""
    if learned is not None and learned.reliable:
        # The home follows the cold: without that day's cold, the same weekdays would mistake a mild day for an absence.
        if cold.get(day) is None:
            return None
        return learned.rest_kwh + learned.per_degree_kwh * max(0.0, cold[day]), True
    same = [used[d] for d in (day - timedelta(days=7 * k) for k in range(1, 5)) if d in used]
    if len(same) < 3:
        return None
    return statistics.median(same), False


def check(day: date, used: dict[date, float], learned: Learned | None, cold: dict[date, float]) -> Unusual | None:
    """`day` (a complete day) when it is unusual, else None."""
    if day not in used:
        return None
    found = usual(day, used, learned, cold)
    if found is None:
        return None
    expected, with_cold = found
    gap = used[day] - expected
    if abs(gap) < MIN_KWH or abs(gap) < SHARE * expected:
        return None
    return Unusual(gap > 0, used[day], expected, with_cold)


# --- The forgotten device (5.2): on far longer than it usually runs ------------------------------------------------

ON_W = 50.0          # a device draws at least this much when it runs
MIN_RUNS = 20        # runs seen before its usual length is trusted
ALWAYS_ON = 0.5      # on more than half the hours: a box, a server; never « forgotten »


def _column(rows):
    """The device's mean power hour by hour, NaN where unknown."""
    if not isinstance(rows, Rows):
        return [NAN if r.get("mean") is None else r["mean"] for r in rows]
    found = rows.column("mean")
    return found if found is not None else []


def _runs(rows: list[dict]) -> tuple[list[int], int, int]:
    """The device's runs (hours on in a row), the hours on and the hours known."""
    runs, current, on, known = [], 0, 0, 0
    for mean in _column(rows):
        if mean != mean:              # NaN: no mean that hour
            continue
        known += 1
        if mean >= ON_W:
            current += 1
            on += 1
        elif current:
            runs.append(current)
            current = 0
    return runs, on, known


def run_limit(rows: list[dict]) -> int | None:
    """How long the device may stay on before Hestia asks « Oublié ? »: twice its long runs (the 95th centile), and
    at least three hours more. None for a device always on, or with too few runs to know. On Frank's real year about
    ten times: the oven 7 h, the TV 11 h, the fridge 6 h without a stop."""
    runs, on, known = _runs(rows)
    if len(runs) < MIN_RUNS or not known or on / known > ALWAYS_ON:
        return None
    ordered = sorted(runs)
    p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    return max(2 * p95, p95 + 3)


def trailing_hours(rows: list[dict]) -> int:
    """The whole hours the device has been on in a row, up to its last known hour."""
    count = 0
    for mean in reversed(_column(rows)):
        if mean != mean or mean < ON_W:
            break
        count += 1
    return count
