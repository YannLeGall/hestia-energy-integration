"""The contract, its prices and its off-peak hours; the euros of any energy (lots 2.1, 3.1, 3.4, 4.2).

Prices come first from the Energy page (an entity or a number the user wrote), then from the regulated tariffs embedded
in the brick (D15, data/tarifs-reglementes.json), then from the settings. A price never known is never zero: the euros
of that energy are unknown and said so (principle 4).

Off-peak hours are read on the meter when it says so (TIC), else learned from the statistics when the page has one
meter per period (Frank's LiXee): each hour of the day, the off-peak meter's share of the energy. A cut inside an hour
gives its minute: 81 % off-peak from midnight to one o'clock means the off-peak hours start near 0:11.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, tzinfo
from functools import lru_cache
import json
from pathlib import Path

from .stats import Series

BASE, HPHC, TEMPO = "base", "hphc", "tempo"
HP, HC = "hp", "hc"
COLORS = ("bleu", "blanc", "rouge")
_TABLE = Path(__file__).parent / "data" / "tarifs-reglementes.json"


# --- The regulated tariffs (D15) --------------------------------------------------------------------------------

def load_regulated(path: Path = _TABLE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


_PERIODS: dict[tuple[int, date], dict | None] = {}


def _period_of(table: dict, day: date) -> dict | None:
    """The table's period holding that day, looked up once per day (each hour of a year asked it again before)."""
    key = (id(table), day)
    if key not in _PERIODS:
        if len(_PERIODS) > 5000:
            _PERIODS.clear()
        _PERIODS[key] = _find_period(table, day)
    return _PERIODS[key]


def _find_period(table: dict, day: date) -> dict | None:
    for period in table.get("periodes", []):
        start = date.fromisoformat(period["debut"])
        end = date.fromisoformat(period["fin"]) if period.get("fin") else None
        if start <= day and (end is None or day <= end):
            return period
    return None


def regulated_price(table: dict, day: date, option: str, kva: int, period: str | None = None, color: str | None = None) -> float | None:
    """The regulated price of one kWh on that day, or None when the table does not know it."""
    grid = (_period_of(table, day) or {}).get(option)
    if not grid:
        return None
    prices = grid.get("prix") or {}
    if option == BASE:
        return prices.get(str(kva))
    if option == HPHC:
        return prices.get(period)
    if option == TEMPO and color in COLORS:
        return (prices.get(color) or {}).get(period)
    return None


def regulated_subscription(table: dict, day: date, option: str, kva: int) -> float | None:
    """The yearly subscription, or None (February 2026 is not in the table yet)."""
    grid = (_period_of(table, day) or {}).get(option)
    yearly = (grid or {}).get("abonnement_an")
    return None if not yearly else yearly.get(str(kva))


# --- The off-peak hours -----------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Range:
    """Off-peak hours from `start` to `end`, local minutes from midnight; `end` < `start` when it crosses midnight."""
    start: int
    end: int

    def contains(self, minute: int) -> bool:
        if self.start <= self.end:
            return self.start <= minute < self.end
        return minute >= self.start or minute < self.end

    def label(self) -> tuple[str, str]:
        return clock(self.start), clock(self.end)

    @property
    def minutes(self) -> int:
        return (self.end - self.start) % 1440


# Weekends and public holidays: some offers (Enercoop « 2 saisons », issue 18) are off-peak all day long.
WEEKEND_ALL, WEEKEND_SAME = "tout", "pareil"


@lru_cache(maxsize=32)
def holidays(year: int) -> frozenset[date]:
    """The eleven French public holidays of a year, Easter worked out (anonymous Gregorian algorithm)."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 19 * l) // 433
    month = (h + l - 7 * m + 90) // 25
    easter = date(year, month, (h + l - 7 * m + 33 * month + 19) % 32)
    fixed = [(1, 1), (5, 1), (5, 8), (7, 14), (8, 15), (11, 1), (11, 11), (12, 25)]
    return frozenset([date(year, mo, da) for mo, da in fixed]
                     + [easter + timedelta(days=n) for n in (1, 39, 50)])  # Easter Monday, Ascension, Whit Monday


def rest_day(day: date) -> bool:
    """Saturday, Sunday or a French public holiday."""
    return day.weekday() >= 5 or day in holidays(day.year)


def parse_offpeak(text: str | None) -> OffPeak | None:
    """The off-peak hours the household typed (« 22:00-06:00 », « 1:30-7:30, 12:30-14:30 »), or None."""
    import re
    ranges = []
    for a, b in re.findall(r"(\d{1,2}[:h]\d{0,2})\s*-\s*(\d{1,2}[:h]\d{0,2})", text or ""):
        def minutes(x: str) -> int:
            h, _, m = x.replace("h", ":").partition(":")
            return int(h) % 24 * 60 + int(m or 0)
        ranges.append(Range(minutes(a), minutes(b)))
    return OffPeak(tuple(ranges), "réglage") if ranges else None


def clock(minute: int) -> str:
    """« 0 h 10 », « 22 h » (PHRASES.md rule 7: a change of price is said to the minute)."""
    h, m = divmod(minute % 1440, 60)
    return f"{h} h {m:02d}" if m else f"{h} h"


@dataclass(frozen=True)
class OffPeak:
    ranges: tuple[Range, ...]
    source: str               # « compteur » (read on the TIC), « appris » (learned from the meters), « réglage », « table »
    days: int = 0             # days the learning used
    shares: tuple[float, ...] = ()  # learned: the off-peak share of each local hour, 0 to 23
    # Weekends and public holidays off-peak all day (issue 18); else the same hours every day.
    weekend_all: bool = False

    def contains(self, at: datetime, tz: tzinfo) -> bool:
        local = at.astimezone(tz)
        if self.weekend_all and rest_day(local.date()):
            return True
        return any(r.contains(local.hour * 60 + local.minute) for r in self.ranges)


def with_weekend(offpeak: OffPeak | None, choice: str | None, found: OffPeak | None = None) -> OffPeak | None:
    """The household's choice for weekends and holidays (« tout », « pareil »); None: what the meters showed."""
    if offpeak is None:
        return None
    weekend_all = choice == WEEKEND_ALL if choice in (WEEKEND_ALL, WEEKEND_SAME) else bool(found and found.weekend_all)
    if weekend_all == offpeak.weekend_all:
        return offpeak
    return OffPeak(offpeak.ranges, offpeak.source, offpeak.days, offpeak.shares, weekend_all)


# Below this share an hour is peak, above (1 - it) off-peak; between, the cut is inside the hour.
_EDGE = 0.04


def learn_offpeak(peak: Series, offpeak: Series, tz: tzinfo, end: datetime | None = None, days: int = 28) -> OffPeak | None:
    """The off-peak hours as the two meters show them over the last `days` days (F1.5, lot 3.4).

    None when the meters do not show it: fewer than 7 days, or no clear off-peak hour.
    Weekends and public holidays off-peak all day long (issue 18) are found apart: the hours are then learned on the
    working days only. Otherwise every day counts, as before.
    """
    end = end or max((h.start for h in [*peak.hours, *offpeak.hours]), default=None)
    if end is None:
        return None
    start = end - timedelta(days=days)
    # [peak, off-peak] energy of each local hour, on working days and on rest days
    work = [[0.0, 0.0] for _ in range(24)]
    rest = [[0.0, 0.0] for _ in range(24)]
    seen: set[date] = set()
    for index, series in ((0, peak), (1, offpeak)):
        for hour in series.hours:
            if hour.kwh is None or hour.hours != 1 or not (start < hour.start <= end):
                continue
            local = hour.start.astimezone(tz)
            (rest if rest_day(local.date()) else work)[local.hour][index] += hour.kwh
            seen.add(local.date())
    if len(seen) < 7:
        return None
    rest_days = sum(1 for d in seen if rest_day(d))
    rest_shares = [(hc / (hp + hc)) if hp + hc > 0 else None for hp, hc in rest]
    # Every hour of the rest days off-peak (a few hours without energy allowed), on at least two of them.
    weekend_all = (rest_days >= 2 and len(seen) - rest_days >= 5 and sum(s is not None for s in rest_shares) >= 20
                   and all(s is None or s >= 1 - _EDGE for s in rest_shares))
    energy = work if weekend_all else [[w[0] + r[0], w[1] + r[1]] for w, r in zip(work, rest)]
    shares = tuple((hc / (hp + hc)) if hp + hc > 0 else None for hp, hc in energy)
    full = [s is not None and s >= 1 - _EDGE for s in shares]
    if not any(full):
        return None
    ranges = []
    for h in range(24):
        if not full[h] or full[(h - 1) % 24]:
            continue
        first = last = h
        while full[(last + 1) % 24] and (last + 1) % 24 != first:
            last = (last + 1) % 24
        before, after = shares[(first - 1) % 24], shares[(last + 1) % 24]
        begin = first * 60 - (round(before * 60) if before and before > _EDGE else 0)
        finish = (last + 1) * 60 + (round(after * 60) if after and after > _EDGE else 0)
        ranges.append(Range(begin % 1440, finish % 1440))
    return OffPeak(tuple(ranges), "appris", len(seen), tuple(0.0 if s is None else round(s, 3) for s in shares), weekend_all)


def next_change(offpeak: OffPeak | None, at: datetime, tz: tzinfo) -> tuple[datetime, str] | None:
    """The next change of period after `at`, to the minute, and the period it starts: (instant, « hc » or « hp »)."""
    if not offpeak or not offpeak.ranges:
        return None
    local = at.astimezone(tz).replace(second=0, microsecond=0)
    now_in = offpeak.contains(local, tz)
    # Five days: a weekend off-peak all day next to a holiday runs from Friday to Tuesday morning.
    for step in range(1, (5 if offpeak.weekend_all else 2) * 1440 + 1):
        moment = local + timedelta(minutes=step)
        if offpeak.contains(moment, tz) != now_in:
            return moment, (HP if now_in else HC)
    return None


# --- The contract and its euros ---------------------------------------------------------------------------------

@dataclass
class Contract:
    """The household's contract (a setting with defaults, filled from what Home Assistant knows)."""
    option: str = HPHC
    kva: int = 6
    offpeak: OffPeak | None = None
    # Prices the user or the Energy page gave, per period (« hp », « hc », « base », or « bleu_hp »…); else the table.
    prices: dict = field(default_factory=dict)
    subscription_year: float | None = None
    export_price: float | None = None
    # Tempo: the colour of each Tempo day seen ({date: « bleu »…}, a Tempo day from 6 h to 6 h); a day without its
    # colour has no price, never the blue one by default.
    colors: dict = field(default_factory=dict)
    # A home that sends its surplus to the grid pays the « majoration auto-producteur » (CRE, 9,60 € HT a year).
    self_producer: bool = False
    # The price of each meter, by its statistic, when the page has several meters for one period (issue 18: a Linky
    # with a register per season and one for the peak days, each with its own price on the Energy page). A meter only
    # counts its own period, so its energy takes its own price, never the one of another register of that period.
    meter_prices: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Euros:
    eur: float
    unknown_kwh: float        # energy whose price was not known: never counted as free
    unknown_hours: int        # hours with no trustworthy energy

    @property
    def complete(self) -> bool:
        return self.unknown_kwh == 0 and self.unknown_hours == 0


def price_at(contract: Contract, table: dict, at: datetime, tz: tzinfo, period: str | None = None, color: str | None = None) -> float | None:
    """The price of one kWh at that instant. `period`: when the meter itself says it (one meter per period)."""
    day = at.astimezone(tz).date()
    if contract.option == BASE:
        return contract.prices.get(BASE) or regulated_price(table, day, BASE, contract.kva)
    if period is None:
        if contract.offpeak is None:
            return None
        period = HC if contract.offpeak.contains(at, tz) else HP
    if contract.option == HPHC:
        return contract.prices.get(period) or regulated_price(table, day, HPHC, contract.kva, period)
    if contract.option == TEMPO:
        if color is None:
            return None
        return contract.prices.get(f"{color}_{period}") or regulated_price(table, day, TEMPO, contract.kva, period, color)
    return None


def cost(contract: Contract, table: dict, tz: tzinfo, metered: list[tuple[Series, str | None]],
         start: datetime, end: datetime, colors: dict | None = None) -> Euros:
    """The euros of the energy bought between two instants, subscription not included.

    `metered`: each import meter and the period it counts (« hp », « hc »), or None when it counts everything.
    `colors`: the Tempo colour of each Tempo day ({date: « bleu »…}); a Tempo day runs from 6 h to 6 h.
    A meter with its own price (`Contract.meter_prices`) is counted at that price.
    """
    eur, unknown_kwh, unknown_hours = 0.0, 0.0, 0
    for series, period in metered:
        for hour in series.between(start, end):
            if hour.kwh is None:
                unknown_hours += hour.hours
                continue
            # A whole day in one step (HA Linky's older days): which part was off-peak is not known, so its price is not.
            if hour.hours > 1 and period is None and contract.option != BASE:
                unknown_kwh += hour.kwh
                continue
            color = None
            if colors is not None:
                color = colors.get((hour.start.astimezone(tz) - timedelta(hours=6)).date())
            price = contract.meter_prices.get(series.stat)
            if price is None:
                price = price_at(contract, table, hour.start, tz, period, color)
            if price is None:
                unknown_kwh += hour.kwh
            else:
                eur += hour.kwh * price
    return Euros(eur, unknown_kwh, unknown_hours)


def self_producer_extra(table: dict, day: date) -> float | None:
    """The « majoration auto-producteur » (TTC a year) on that day, or None when the table does not know it."""
    for item in table.get("majoration_autoproducteur") or []:
        if item["debut"] <= day.isoformat() and (item.get("fin") is None or day.isoformat() <= item["fin"]):
            return item["ttc_an"]
    return None


def regulated_today(contract: Contract, table: dict, day: date) -> bool:
    """The prices the page shows today are the regulated ones of that day (Tarif EDF, a price helper): the household is
    on the regulated tariff, so each past day takes the table's price of its own day, never today's."""
    if not contract.prices:
        return False
    for key, value in contract.prices.items():
        period = None if key == BASE else key
        known = regulated_price(table, day, contract.option, contract.kva, period)
        if known is None or abs(known - value) > 0.0005:
            return False
    return True


def subscription(contract: Contract, table: dict, day: date) -> float | None:
    """The subscription's share of one day, or None when not known."""
    yearly = contract.subscription_year or regulated_subscription(table, day, contract.option, contract.kva)
    if yearly is None:
        return None
    if contract.self_producer and not contract.subscription_year:
        extra = self_producer_extra(table, day)
        if extra is None:
            return None
        yearly += extra
    days = 366 if (day.year % 4 == 0 and (day.year % 100 != 0 or day.year % 400 == 0)) else 365
    return yearly / days


def day_bounds(day: date, tz: tzinfo) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time(0), tz)
    return start, datetime.combine(day + timedelta(days=1), time(0), tz)
