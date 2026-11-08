"""The night baseload: what the home draws when everybody sleeps, in W and in euros a year, and its drift (lot 2.4).

Read on the energy bought hour by hour between midnight and 6 h, over the last 28 nights: the 5th centile of those
168 hours. Not each night's lowest hour, which winter heating lifts: on Frank's home the nightly lowest hour reads
600 W in January and 250 W in June, the 5th centile 230 to 260 W all year. Night hours have no sun: what is bought is
what is used (level 0 is enough), but it needs hourly data (« disponible quand la demi-heure arrive »).

The drift compares today's baseload with the lowest of the past months (`veille_hausse`, PHRASES.md § 3.2): only a rise
held for 7 days and larger than 30 W and 15 % is said.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta, tzinfo

from .stats import Series

NIGHT = (0, 6)            # local hours, start included, end excluded
WINDOW_DAYS = 28
MIN_NIGHTS = 14
CENTILE = 0.05
RISE_W = 30
RISE_SHARE = 0.15
HELD_DAYS = 7


@dataclass(frozen=True)
class Baseload:
    watts: float
    nights: int
    end: date


def baseload(series: Series, tz: tzinfo, end: date | None = None) -> Baseload | None:
    """The baseload of the 28 nights before `end` (included), or None with fewer than 14 nights of hourly data."""
    hours: list[tuple[date, float]] = []
    for hour in series.hours:
        if hour.kwh is None or hour.hours != 1:
            continue
        local = hour.start.astimezone(tz)
        if NIGHT[0] <= local.hour < NIGHT[1]:
            hours.append((local.date(), hour.kwh))
    if not hours:
        return None
    end = end or max(d for d, _ in hours)
    window = [(d, kwh) for d, kwh in hours if end - timedelta(days=WINDOW_DAYS) < d <= end]
    nights = len({d for d, _ in window})
    if nights < MIN_NIGHTS:
        return None
    values = sorted(kwh for _, kwh in window)
    return Baseload(round(values[int(len(values) * CENTILE)] * 1000), nights, end)


def yearly_euros(watts: float, price_per_kwh: float | None) -> float | None:
    """What a constant power costs in a year at that price (an average of the contract's prices)."""
    if price_per_kwh is None:
        return None
    return watts / 1000 * 24 * 365 * price_per_kwh


def average_price(hp: float | None, hc: float | None, offpeak_hours: float = 8) -> float | None:
    """The price of a constant power over a day: peak and off-peak hours in their share of the day."""
    if hp is None or hc is None:
        return hp if hc is None else hc
    return (hp * (24 - offpeak_hours) + hc * offpeak_hours) / 24


@dataclass(frozen=True)
class Rise:
    watts: float              # today's baseload
    reference: float          # the lowest one of the months before
    since: date               # the end of the reference window: « plus qu'en {mois} »


def rise(series: Series, tz: tzinfo, end: date, months: int = 12) -> Rise | None:
    """A rise of the baseload held for 7 days against the lowest 28-night baseload of the past months, or None."""
    now = [baseload(series, tz, end - timedelta(days=k)) for k in range(HELD_DAYS)]
    if any(b is None for b in now):
        return None
    current = min(b.watts for b in now)
    past = [baseload(series, tz, end - timedelta(days=WINDOW_DAYS * k)) for k in range(2, months + 1)]
    past = [b for b in past if b is not None]
    if not past:
        return None
    lowest = min(past, key=lambda b: b.watts)
    if current - lowest.watts >= RISE_W and current >= lowest.watts * (1 + RISE_SHARE):
        return Rise(current, lowest.watts, lowest.end)
    return None
