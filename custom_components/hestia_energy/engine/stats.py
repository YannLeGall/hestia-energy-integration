"""Energy hour by hour from Home Assistant's long-term statistics, and the totals of any period (lot 1.3).

The recorder keeps, for a meter, a cumulative `sum` per hour; an hour's energy is the step from one hour to the next.
No `utility_meter`, no SQL sensor: the same statistics the Energy page draws, kept 11 to 24 months.

A step that cannot be true is never counted (lot 1.4): more than the meter can physically pass in an hour (the
subscribed power for the grid, the panels for the export), or a meter going back. The hour is then unknown, not zero:
a day with an unknown hour says so, it is never made up.
"""
from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass, field
from datetime import date, datetime, tzinfo
from operator import attrgetter

from .rows import Rows, when

_START = attrgetter("start")


@dataclass(frozen=True, slots=True)
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
    # What is worked out once from the hours (their order, each local day's total, the night hours), kept while the
    # hours stay the same list of the same length (audit of 9 Nov. 2026: each total read the whole year again).
    _memo: dict = field(default_factory=dict, repr=False, compare=False)

    def known(self) -> list[Hour]:
        return [h for h in self.hours if h.kwh is not None]

    def memo(self, key, make):
        """`make()` once for these hours; worked out again when the hours change (another list, another length)."""
        stamp = (id(self.hours), len(self.hours))
        if self._memo.get("_stamp") != stamp:
            self._memo = {"_stamp": stamp}
        if key not in self._memo:
            self._memo[key] = make()
        return self._memo[key]

    def between(self, start: datetime, end: datetime) -> list[Hour]:
        """The hours starting from `start` (included) to `end` (excluded), found by halving: the hours are in order."""
        hours = self.hours
        if not self.memo("ordered", lambda: all(a.start <= b.start for a, b in zip(hours, hours[1:]))):
            return [h for h in hours if start <= h.start < end]
        return hours[bisect_left(hours, start, key=_START):bisect_left(hours, end, key=_START)]


# A meter going back by less than this in an hour is a correction, read as zero; more is a reset, the hour unknown.
BACK_TOLERANCE_KWH = 2.0


def steps(rows) -> list[tuple[float, float, int]]:
    """Each step of the meter's sum from one row to the next: (start of the hour in seconds, kWh, hours it covers)."""
    rows = Rows.of(rows)
    sums, ts = rows.column("sum"), rows.ts
    out = []
    if sums is None:
        return out
    for i in range(1, len(ts)):
        a, b = sums[i - 1], sums[i]
        if a != a or b != b:          # NaN: no sum that hour
            continue
        out.append((ts[i], b - a, max(1, round((ts[i] - ts[i - 1]) / 3600))))
    return out


def energy(stat: str, rows, limit_kwh=None, steps_=None) -> Series:
    """Each hour's energy from the recorder's rows ({start, sum}, in order).

    `limit_kwh`: the most this meter can pass in one hour — a number, or a function of the hour's start (the export
    limited by that hour's sun); a function may also read the hour by its start in seconds (`by_ts`). None: the
    meter's own history decides (`robust_limit`). `steps_`: the rows' steps when already worked out.
    """
    series = Series(stat)
    found = steps(rows) if steps_ is None else steps_
    if limit_kwh is None:
        fixed = robust_limit([d for _, d, span in found if span == 1])
        limit = lambda stamp: fixed  # noqa: E731
    elif callable(limit_kwh):
        by_ts = getattr(limit_kwh, "by_ts", None)
        limit = by_ts if by_ts is not None else (lambda stamp: limit_kwh(when(stamp)))
    else:
        limit = lambda stamp: limit_kwh  # noqa: E731
    for stamp, delta, span in found:
        start = when(stamp)
        most = limit(stamp)
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
    for hour in series.between(start, end):
        hours += hour.hours
        if hour.kwh is None:
            unknown += hour.hours
        else:
            kwh += hour.kwh
    return Total(kwh, unknown, hours)


def days(series: Series, tz: tzinfo) -> dict[date, Total]:
    """Each local day's total (the day of the hour's beginning, in the home's time zone)."""
    return dict(series.memo(("days", tz), lambda: _days(series, tz)))


def local_hours(series: Series, tz: tzinfo) -> list[tuple[datetime, Hour]]:
    """Each hour with its local start, worked out once for these hours."""
    return series.memo(("local", tz), lambda: [(h.start.astimezone(tz), h) for h in series.hours])


def _days(series: Series, tz: tzinfo) -> dict[date, Total]:
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
    rows = Rows.of(rows)
    highest = rows.column("max")
    # The highest power of each hour and of the `lag_hours` before it, worked out in one pass over the hours.
    window: dict[float, float] = {}
    if highest is not None:
        for stamp, peak in zip(rows.ts, highest):
            if peak != peak:
                continue
            peak = abs(peak)
            for k in range(lag_hours + 1):
                key = stamp + 3600 * k
                if peak > window.get(key, -1.0):
                    window[key] = peak

    def by_ts(stamp: float) -> float | None:
        peak = window.get(stamp)
        if peak is None:
            return None
        return (peak / 1000 * margin + slack_kwh) / factor

    def limit(start: datetime) -> float | None:
        return by_ts(start.timestamp())
    limit.by_ts = by_ts
    return limit
