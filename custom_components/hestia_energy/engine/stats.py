"""Energy hour by hour from Home Assistant's long-term statistics, and the totals of any period (lot 1.3).

The recorder keeps, for a meter, a cumulative `sum` per hour; an hour's energy is the step from one hour to the next.
No `utility_meter`, no SQL sensor: the same statistics the Energy page draws, kept 11 to 24 months.

A step that cannot be true is never counted (lot 1.4): more than the meter can physically pass in an hour (the
subscribed power for the grid, the panels for the export), or a meter going back. The hour is then unknown, not zero:
a day with an unknown hour says so, it is never made up.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, tzinfo


@dataclass(frozen=True)
class Hour:
    start: datetime          # aware, the hour's beginning
    kwh: float | None        # None: unknown (a jump or a meter reset)
    hours: int = 1           # >1 when the statistics skipped hours: the step covers them all


@dataclass(frozen=True)
class Jump:
    """A step that cannot be true: kept for the panel (PHRASES.md, p_compteur_saut), never counted."""
    start: datetime
    kwh: float
    limit: float


@dataclass
class Series:
    stat: str
    hours: list[Hour] = field(default_factory=list)
    jumps: list[Jump] = field(default_factory=list)
    # Small steps back (a cloud meter correcting itself): read as zero, counted here.
    backs: int = 0

    def known(self) -> list[Hour]:
        return [h for h in self.hours if h.kwh is not None]


# A meter going back by less than this in an hour is a correction, read as zero; more is a reset, the hour unknown.
BACK_TOLERANCE_KWH = 2.0


def energy(stat: str, rows: list[dict], limit_kwh=None) -> Series:
    """Each hour's energy from the recorder's rows ({start, sum}, in order).

    `limit_kwh`: the most this meter can pass in one hour — a number, or a function of the hour's start (the export
    limited by that hour's sun). None: the meter's own history decides (`robust_limit`).
    """
    series = Series(stat)
    steps = []
    for before, after in zip(rows, rows[1:]):
        if before.get("sum") is None or after.get("sum") is None:
            continue
        span = max(1, round((after["start"] - before["start"]) / timedelta(hours=1)))
        steps.append((after["start"], after["sum"] - before["sum"], span))
    if limit_kwh is None:
        fixed = robust_limit([d for _, d, span in steps if span == 1])
        limit = lambda start: fixed  # noqa: E731
    elif callable(limit_kwh):
        limit = limit_kwh
    else:
        limit = lambda start: limit_kwh  # noqa: E731
    for start, delta, span in steps:
        most = limit(start)
        if delta < 0:
            if -delta <= BACK_TOLERANCE_KWH:
                series.backs += 1
                series.hours.append(Hour(start, 0.0, span))
            else:
                series.hours.append(Hour(start, None, span))
        elif most is not None and delta > most * span:
            series.jumps.append(Jump(start, delta, most))
            series.hours.append(Hour(start, None, span))
        else:
            series.hours.append(Hour(start, delta, span))
    return series


def robust_limit(deltas: list[float]) -> float | None:
    """When no physical limit is known: ten times the 99th centile of the meter's own hours, at least 1 kWh.

    The 99th, not higher: a year has more than 1 % of quiet hours but jumps are a handful (Frank's peak meter: 10 jumps
    of about 5 400 kWh in 8 760 hours, which are the 99.9th centile themselves; its 99th centile is 4.9 kWh).
    """
    positive = sorted(d for d in deltas if d > 0)
    if len(positive) < 48:
        return None
    centile = positive[min(len(positive) - 1, int(len(positive) * 0.99))]
    return max(1.0, 10 * centile)


@dataclass(frozen=True)
class Total:
    kwh: float
    unknown_hours: int     # hours of the period with no trustworthy value
    hours: int             # hours of the period covered by the statistics

    @property
    def complete(self) -> bool:
        return self.unknown_hours == 0


def total(series: Series, start: datetime, end: datetime) -> Total:
    """Energy between two instants (start included, end excluded)."""
    kwh, unknown, hours = 0.0, 0, 0
    for hour in series.hours:
        if start <= hour.start < end:
            hours += hour.hours
            if hour.kwh is None:
                unknown += hour.hours
            else:
                kwh += hour.kwh
    return Total(kwh, unknown, hours)


def days(series: Series, tz: tzinfo) -> dict[date, Total]:
    """Each local day's total (the day of the hour's beginning, in the home's time zone)."""
    out: dict[date, tuple] = {}
    for hour in series.hours:
        day = hour.start.astimezone(tz).date()
        kwh, unknown, hours = out.get(day, (0.0, 0, 0))
        if hour.kwh is None:
            out[day] = (kwh, unknown + hour.hours, hours + hour.hours)
        else:
            out[day] = (kwh + hour.kwh, unknown, hours + hour.hours)
    return {d: Total(*v) for d, v in out.items()}


def months(series: Series, tz: tzinfo) -> dict[tuple[int, int], Total]:
    out: dict[tuple[int, int], Total] = {}
    for day, t in days(series, tz).items():
        key = (day.year, day.month)
        prev = out.get(key, Total(0.0, 0, 0))
        out[key] = Total(prev.kwh + t.kwh, prev.unknown_hours + t.unknown_hours, prev.hours + t.hours)
    return out


def merge(*series: Series) -> Series:
    """Several meters of one thing (Frank's peak and off-peak meters) as one: an hour is unknown if one says so.

    An hour missing from one meter's statistics is not unknown: that meter's next step covers it (`Hour.hours`).
    """
    by_start: dict[datetime, list] = {}
    for s in series:
        for hour in s.hours:
            by_start.setdefault(hour.start, []).append(hour)
    merged = Series("+".join(s.stat for s in series), backs=sum(s.backs for s in series),
                    jumps=sorted((j for s in series for j in s.jumps), key=lambda j: j.start))
    for start in sorted(by_start):
        hours = by_start[start]
        unknown = any(h.kwh is None for h in hours)
        merged.hours.append(Hour(start, None if unknown else sum(h.kwh for h in hours), max(h.hours for h in hours)))
    return merged


def limit_from_power(rows: list[dict], lag_hours: int = 2, margin: float = 1.5, slack_kwh: float = 0.1, factor: float = 1.0):
    """A meter's physical limit from its own power: an hour cannot hold more than the highest power seen in it (or in the
    `lag_hours` before, for a cloud meter that comes late), with a margin. `factor`: the meter's scale (1/1000 in Wh).

    Frank's fridge: about 0.02 kWh an hour, and 87 hours of 27 to 300 kWh when its meter took its index again.
    Returns a function of the hour's start, for `energy`; None for an hour without power (no limit then).
    """
    peaks = {r["start"]: r["max"] for r in rows if r.get("max") is not None}

    def limit(start: datetime) -> float | None:
        seen = [peaks.get(start - timedelta(hours=k)) for k in range(lag_hours + 1)]
        seen = [abs(p) for p in seen if p is not None]
        if not seen:
            return None
        return (max(seen) / 1000 * margin + slack_kwh) / factor
    return limit
