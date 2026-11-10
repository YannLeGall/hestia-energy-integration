"""The health of the data, told before any figure (lot 1.4, principle 4: right before pretty).

Each check reads the long-term statistics only, so it is replayed on real data and works at level 0. The card stays
silent about what is found; the panel says it (PHRASES.md § 7).

- `scale`: a meter in Wh read as kWh (Frank's washing machine: a thousand times too much) — told by its own power;
- `lag`: a meter whose statistics arrive an hour late (Comwatt's cloud) — told by its own power;
- `since`: a meter younger than the period asked (« since 25 August », never « this year »);
- `frozen`: a power stuck at one value for hours while its own meter moves;
- `impossible`: measured devices using more than the whole home on a day.
The jumps no meter can make are set aside by stats.energy.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, tzinfo
from statistics import median

from .rows import Rows, when
from .stats import Series


def _power_by_hour(rows) -> dict[float, float]:
    """Each hour's mean power, by the hour's start in seconds."""
    rows = Rows.of(rows)
    means = rows.column("mean")
    if means is None:
        return {}
    return {t: m for t, m in zip(rows.ts, means) if m == m}


def _ratios(series: Series, power: dict[float, float], shift: int, floor_w: float) -> list[float]:
    """Each hour's energy over the energy its power says, the power read `shift` hours earlier."""
    out = []
    back = 3600 * shift
    for hour in series.hours:
        if hour.kwh is None or hour.kwh <= 0 or hour.hours != 1:
            continue
        watts = power.get(hour.start.timestamp() - back)
        if watts is not None and abs(watts) >= floor_w:
            out.append(hour.kwh / (abs(watts) / 1000))
    return out


class Ratios:
    """The ratios of one meter to its power at each shift, worked out once for `scale` and `lag` together."""

    def __init__(self, series: Series, power_rows, floor_w: float = 200) -> None:
        self.series, self.power, self.floor_w, self._found = series, _power_by_hour(power_rows), floor_w, {}

    def at(self, shift: int) -> list[float]:
        if shift not in self._found:
            self._found[shift] = _ratios(self.series, self.power, shift, self.floor_w)
        return self._found[shift]


# Scales a meter can be in by mistake: its median ratio to its power.
_SCALES = (1000.0, 0.001)


def scale(series: Series, power_rows, floor_w: float = 200, ratios_: Ratios | None = None) -> float:
    """The factor that brings this meter to kWh: 1, or 1/1000 for a meter in Wh read as kWh. Needs 24 busy hours."""
    found = ratios_ or Ratios(series, power_rows, floor_w)
    for shift in (0, 1, 2):
        ratios = found.at(shift)
        if len(ratios) < 24:
            continue
        m = median(ratios)
        for factor in _SCALES:
            if 0.8 * factor <= m <= 1.2 * factor:
                return 1 / factor
    return 1.0


def lag(series: Series, power_rows, floor_w: float = 200, factor: float = 1.0, ratios_: Ratios | None = None) -> int | None:
    """Hours by which the meter's statistics come after its power (0, 1 or 2), or None when its hours are too few.

    The lag that brings each hour's energy closest to the energy its power says, measured as the spread of the ratios
    around 1 (Frank's dishwasher: 0.84 in its own hour, 1.00 one hour later).
    """
    found = ratios_ or Ratios(series, power_rows, floor_w)
    spreads = {}
    for shift in (0, 1, 2):
        ratios = [r * factor for r in found.at(shift)]
        if len(ratios) >= 24:
            spreads[shift] = median(abs(r - 1) for r in ratios)
    if not spreads:
        return None
    best = min(spreads, key=spreads.get)
    # A steady load (water heater) reads alike at every lag: no lag unless it is clearly better.
    if best and 0 in spreads and spreads[best] > 0.6 * spreads[0]:
        return 0
    return best


def since(series: Series, start: datetime, tz: tzinfo) -> date | None:
    """The day the meter starts when it starts after `start` (+ one day of grace), else None."""
    first = next((h.start for h in series.hours), None)
    if first is None or first <= start + timedelta(days=1):
        return None
    return first.astimezone(tz).date()


def frozen(power_rows, series: Series | None, hours: int = 6, factor: float = 1.0) -> list[tuple[datetime, int, float]]:
    """Runs of at least `hours` hours where the power stays at one value while its own meter says otherwise.

    Without a meter, nothing is said: a radiator at 1 000 W for hours is not frozen. Returns (start, hours, value).
    """
    if series is None:
        return []
    rows = Rows.of(power_rows)
    lows, highs = rows.column("min"), rows.column("max")
    if lows is None or highs is None:
        return []
    energy = {h.start.timestamp(): h.kwh * factor for h in series.hours if h.kwh is not None}
    runs, current = [], None
    for stamp, low, high in zip(rows.ts, lows, highs):
        flat = low == low and low == high           # NaN (no minimum) is never flat
        kwh = energy.get(stamp)
        disagrees = flat and kwh is not None and abs(kwh - abs(low) / 1000) > max(0.1, 0.5 * kwh)
        if disagrees and current and current[2] == low and stamp - current[3] <= 3600:
            current = (current[0], current[1] + 1, current[2], stamp)
            continue
        if current and current[1] >= hours:
            runs.append(current[:3])
        current = (stamp, 1, low, stamp) if disagrees else None
    if current and current[1] >= hours:
        runs.append(current[:3])
    return [(when(start), n, value) for start, n, value in runs]


def impossible(home: dict[date, float], devices: dict[date, float], margin: float = 1.05) -> list[date]:
    """Days where the measured devices used more than the whole home (5 % allowed for the meters' own error)."""
    return sorted(d for d, kwh in devices.items() if d in home and kwh > home[d] * margin + 0.2)


# --- Against the bill's own meter (Enedis through HA Linky or MyElectricalData) ----------------------------------

GAP_SHARE = 0.02      # a difference over the year worth saying
DAY_SHARE = 0.25      # a day this far from the bill's meter (and 1.5 kWh at least) is a day the home's meter missed
MIN_DAYS = 30


def against_reference(stat: str, what: str, page_days: dict, reference_days: dict) -> list:
    """The home's meters against the bill's (Enedis fait foi): the gap over the days both know, and the days far off.
    `page_days`, `reference_days`: {date: Total}. `what`: « vos achats » or « votre revente », as said."""
    from .home import Finding
    both = [(d, page_days[d].kwh, reference_days[d].kwh) for d in reference_days
            if d in page_days and page_days[d].complete and reference_days[d].complete]
    if len(both) < MIN_DAYS:
        return []
    page, reference = sum(p for _, p, _ in both), sum(r for _, _, r in both)
    # More than double one way or the other: not the same quantity (a unit, another meter), nothing to compare.
    if reference <= 0 or not 0.5 <= page / reference <= 2:
        return []
    found = []
    if reference > 0 and abs(reference - page) / reference >= GAP_SHARE:
        found.append(Finding("p_reference_ecart", stat, {"source": "Enedis", "quoi": what, "jours": len(both),
                     "pourcent": round(abs(reference - page) / reference * 100), "sens": "plus" if reference > page else "moins"}))
    off = [(d, p, r) for d, p, r in both if abs(r - p) > max(1.5, DAY_SHARE * r)]
    if off:
        d, p, r = max(off, key=lambda x: abs(x[2] - x[1]))
        found.append(Finding("p_reference_jours", stat, {"jours": len(off), "quoi": what, "date": d,
                                                        "page": round(p, 1), "enedis": round(r, 1)}))
    return found
