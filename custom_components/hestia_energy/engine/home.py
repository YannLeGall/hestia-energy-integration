"""The home's energy, put together from the Energy page and the statistics: one truth per quantity (lots 1.2 to 1.4).

Each meter of the page is read with its own physical limit, so an impossible hour is unknown, never counted:
- bought from the grid: the subscribed power (9 kWh in an hour for 9 kVA), else the meter's own history;
- sent to the grid: the sun of that hour and the two before (a cloud meter comes late), else the meter's own history;
- a measured device: its own highest power in that hour and the two before;
- the panels: their own history (their peak power is not in the page), checked hour by hour against the inverters'
  own channels when an extension gives them (OpenDTU): an hour where the page says much less than the inverters is
  taken from the inverters (Frank's page said 0 kWh from 11 to 18 March while the panels produced).
Each meter's scale (Wh read as kWh) and lag (statistics an hour late) are told by its own power. What is found becomes
a `Finding` for the panel; the card stays silent.

The home's consumption is bought + produced − sent: the page's own definition.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone, tzinfo

from . import health, stats
from .rows import Rows, when
from .sources import EnergyPage, Meter
from .stats import Hour, Series, Total


@dataclass
class Finding:
    """Something the panel says about the data: a phrase id (PHRASES.md § 7) and its values."""
    id: str
    stat: str
    values: dict = field(default_factory=dict)


@dataclass
class Reading:
    meter: Meter
    series: Series            # in kWh (or the page's unit for water), impossible hours unknown
    factor: float = 1.0       # what the statistics were multiplied by (1/1000 for a meter in Wh read as kWh)
    lag: int | None = None    # hours the statistics come after the power
    since: date | None = None


@dataclass
class Home:
    page: EnergyPage
    tz: tzinfo
    readings: dict[str, Reading] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    bought: Series | None = None
    sent: Series | None = None
    sun: Series | None = None

    def of(self, kind: str) -> list[Reading]:
        return [r for r in self.readings.values() if r.meter.kind == kind]

    def metered(self) -> list[tuple[Series, str | None]]:
        """The import meters with the period each one counts, for tariff.cost."""
        return [(r.series, r.meter.period) for r in self.of("import")]

    def used_days(self) -> dict[date, float]:
        """The whole days known hour by hour (not today, not a day with a gap): each one's consumption in kWh."""
        return {d: t.kwh for d, t in self.consumption_days().items() if t.complete and t.hours >= 23}

    def consumption_days(self) -> dict[date, Total]:
        """Each day's consumption of the whole home; an unknown hour of any part is counted as unknown."""
        if self.bought is None:
            return {}
        out: dict[date, tuple] = {}
        # What was sent comes out of the sun: without the sun measured (HA Linky with a resale), only what was bought is
        # known, and taking the resale out of it would make a summer home use almost nothing.
        parts = ((self.bought, 1), (self.sun, 1), (self.sent, -1)) if self.sun is not None else ((self.bought, 1),)
        for series, sign in parts:
            if series is None:
                continue
            for day, t in stats.days(series, self.tz).items():
                kwh, unknown, hours = out.get(day, (0.0, 0, 0))
                out[day] = (kwh + sign * t.kwh, unknown + t.unknown_hours, max(hours, t.hours))
        return {d: Total(*v) for d, v in out.items()}


def _scaled(series: Series, factor: float) -> Series:
    if factor == 1:
        return series
    out = Series(series.stat, backs=series.backs, jumps=series.jumps)
    out.hours = [Hour(h.start, None if h.kwh is None else h.kwh * factor, h.hours) for h in series.hours]
    return out


def _sun_limit(sun: Series | None, doubtful: set, fallback: float | None, margin: float = 1.1, slack: float = 0.3):
    """What can be sent in an hour: the sun of that hour and the two before, together (a cloud meter comes late and
    then sends two hours in one: Frank's export reads 5.6 kWh in an hour of 4.4 kWh of sun).

    When the sun itself is doubtful (nothing from the inverters, the page at zero), the export meter's own history.
    """
    if sun is None:
        return fallback
    produced = {h.start.timestamp(): h.kwh for h in sun.hours if h.kwh is not None}
    unsure = {t.timestamp() for t in doubtful}

    def by_ts(stamp: float) -> float | None:
        if stamp in unsure or stamp - 3600 in unsure or stamp - 7200 in unsure:
            return fallback
        seen = [produced.get(stamp - 3600 * k) for k in range(3)]
        seen = [v for v in seen if v is not None]
        return sum(seen) * margin + slack if seen else fallback

    def limit(start: datetime) -> float | None:
        return by_ts(start.timestamp())
    limit.by_ts = by_ts
    return limit


def inverter_energy(rows: dict[str, list[dict]], channels: list[str]) -> Series | None:
    """The inverters' production hour by hour, from each channel's mean power (W over one hour = Wh).

    A channel missing in an hour takes its sibling's value (the other input of the same inverter, « _ch1 » / « _ch2 »),
    never zero while the others produce (LISEZMOI: one East channel has 5 070 hours against 8 375).
    """
    means = {}
    for c in channels:
        found = Rows.of(rows.get(c, []))
        column = found.column("mean")
        if column is not None:
            means[c] = {t: m for t, m in zip(found.ts, column) if m == m}
    means = {c: m for c, m in means.items() if m}
    if not means:
        return None
    sibling = {c: next((o for o in means if o != c and o.rsplit("_ch", 1)[0] == c.rsplit("_ch", 1)[0]), None) for c in means}
    out = Series("+".join(means))
    for start in sorted({t for m in means.values() for t in m}):
        total, unknown = 0.0, False
        for c, m in means.items():
            value = m.get(start)
            if value is None and sibling[c]:
                value = means[sibling[c]].get(start)
            if value is None:
                others = [m2.get(start) for m2 in means.values() if m2.get(start) is not None]
                unknown = any(v > 5 for v in others)
                value = 0.0
            total += max(0.0, value) / 1000
        out.hours.append(Hour(when(start), None if unknown else total))
    return out


def _arbitrate_sun(page_sun: Series | None, inverters: Series | None) -> tuple[Series | None, int]:
    """Hour by hour, the page's production unless the inverters show clearly more (30 % and 0.2 kWh): how many hours."""
    if page_sun is None or inverters is None:
        return page_sun or inverters, 0
    other = {h.start: h.kwh for h in inverters.hours if h.kwh is not None}
    out, taken = Series(page_sun.stat, jumps=page_sun.jumps, backs=page_sun.backs), 0
    for hour in page_sun.hours:
        alt = other.get(hour.start)
        if alt is not None and (hour.kwh is None or hour.kwh < 0.7 * alt - 0.2):
            out.hours.append(Hour(hour.start, alt, hour.hours))
            taken += 1
        else:
            out.hours.append(hour)
    return out, taken


def build(page: EnergyPage, rows: dict[str, list[dict]], tz: tzinfo, start: datetime, kva: float | None = None,
          inverters: list[str] = ()) -> Home:
    """Read every meter of the page from its statistics (`rows`: {statistic_id: [{start, mean, min, max, sum}]}).

    `inverters`: the power statistics of each inverter channel, when an extension gives them (OpenDTU), to check the
    page's production hour by hour.
    """
    home = Home(page, tz)
    for remark in page.remarks:
        home.findings.append(Finding(remark.id, remark.values.get("stat", ""), remark.values))

    def read(meter: Meter, limit=None, own_power: bool = False) -> Reading | None:
        if meter.stat in home.readings:
            return home.readings[meter.stat]
        own = rows.get(meter.stat)
        if not own:
            home.findings.append(Finding("p_sans_statistiques", meter.stat, {"nom": meter.name or meter.stat}))
            return None
        power_id = meter.power.rate or meter.power.rate_from
        power = rows.get(power_id, []) if power_id else []
        if power_id and not power:
            home.findings.append(Finding("p_sans_statistiques", power_id, {"nom": meter.name or power_id}))
        factor, lag = 1.0, None
        steps = stats.steps(own)
        if own_power and power:
            raw = stats.energy(meter.stat, own, float("inf"), steps)
            ratios = health.Ratios(raw, power)
            factor = health.scale(raw, power, ratios_=ratios)
            lag = health.lag(raw, power, factor=factor, ratios_=ratios)
            limit = stats.limit_from_power(power, factor=factor)
        series = _scaled(stats.energy(meter.stat, own, limit, steps), factor)
        reading = Reading(meter, series, factor, lag)
        home.readings[meter.stat] = reading
        name = meter.name or meter.stat
        if series.jumps:
            biggest = max(series.jumps, key=lambda j: j.kwh)
            home.findings.append(Finding("p_compteur_saut", meter.stat, {
                "capteur": name, "valeur": round(biggest.kwh * factor, 1), "fois": len(series.jumps),
                "premier": series.jumps[0].start, "dernier": series.jumps[-1].start}))
        if factor != 1:
            home.findings.append(Finding("p_unite", meter.stat, {"capteur": name, "facteur": round(1 / factor)}))
        if lag:
            home.findings.append(Finding("p_cloud_retard", meter.stat, {"source": name, "duree_h": lag}))
        if power:
            unit = "L/min" if meter.kind in ("water", "water_device") else "W"
            for begin, hours, value in health.frozen(power, series):
                home.findings.append(Finding("p_capteur_fige", power_id, {
                    "capteur": name, "valeur": value, "unite": unit, "debut": begin, "heures": hours}))
        return reading

    bought = [read(m, kva) for m in page.imports]
    sun = [read(m) for m in page.solar]
    page_sun = stats.merge(*[r.series for r in sun if r]) if any(sun) else None
    home.sun, taken = _arbitrate_sun(page_sun, inverter_energy(rows, list(inverters)) if inverters else None)
    if taken:
        days = sorted({h.start.astimezone(tz).date() for h, p in zip(home.sun.hours, page_sun.hours) if h is not p})
        home.findings.append(Finding("p_soleil_onduleurs", "", {"heures": taken, "jours": len(days), "liste": days}))
    # Hours the page says no sun and the inverters say nothing (OpenDTU offline, 11 to 18 March): the sun is not known.
    present = {when(t) for c in inverters for t in Rows.of(rows.get(c, [])).ts}
    doubtful = {h.start for h in (home.sun.hours if home.sun else []) if inverters and h.kwh == 0 and h.start not in present}
    fallback = {m.stat: stats.robust_limit([h.kwh for h in stats.energy(m.stat, rows[m.stat], float("inf")).known()])
                for m in page.exports if rows.get(m.stat)}
    sent = [read(m, _sun_limit(home.sun, doubtful, fallback.get(m.stat))) for m in page.exports]
    home.bought = stats.merge(*[r.series for r in bought if r]) if any(bought) else None
    home.sent = stats.merge(*[r.series for r in sent if r]) if any(sent) else None
    if home.sun is not None and home.sent is not None and doubtful:
        exported = {h.start for h in home.sent.hours if h.kwh is not None and h.kwh > 0.2}
        lost = doubtful & exported
        if lost:
            home.sun.hours = [Hour(h.start, None, h.hours) if h.start in lost else h for h in home.sun.hours]
            days = sorted({t.astimezone(tz).date() for t in lost})
            home.findings.append(Finding("p_soleil_manquant", "", {"heures": len(lost), "jours": len(days), "liste": days}))
    for meter in page.devices:
        read(meter, own_power=True)
    for meter in [*page.gas, *page.water]:
        read(meter)
    _since(home, start)
    _impossible(home)
    return home


def _since(home: Home, start: datetime) -> None:
    """A meter younger than the home's own history says since when (« since 25 August », never « this year »).
    The home's history starts with its oldest meter, not with the period asked: a Home Assistant kept for one year has
    no meter « since » the year before."""
    firsts = [r.series.hours[0].start for r in home.readings.values() if r.series.hours]
    if not firsts:
        return
    reference = max(start, min(firsts))
    for reading in home.readings.values():
        reading.since = health.since(reading.series, reference, home.tz)
        if reading.since:
            name = reading.meter.name or reading.meter.stat
            home.findings.append(Finding("p_depuis", reading.meter.stat, {"capteur": name, "date": reading.since}))


def _impossible(home: Home) -> None:
    """Days where the measured devices (sub-meters counted once) used more than the whole home."""
    whole = {d: t.kwh for d, t in home.consumption_days().items() if t.complete}
    devices: dict[date, float] = {}
    for reading in home.of("device"):
        if reading.meter.included_in:
            continue
        for day, t in stats.days(reading.series, home.tz).items():
            devices[day] = devices.get(day, 0.0) + t.kwh
    days = health.impossible(whole, devices)
    if days:
        home.findings.append(Finding("p_somme_impossible", "", {"jours": len(days), "dernier": days[-1], "liste": days}))


# --- Following the bill's meter (Enedis fait foi, decided on 7 Nov. 2026) ------------------------------------------

def follow(home: Home, kind: str, reference: Series) -> Home:
    """The home with its `kind` meters (« import » or « export ») set day by day on Enedis's totals: each day keeps the
    home's own hourly shape (which part was off-peak), scaled to Enedis's total. A day the home's meters nearly missed
    (under 1 kWh, the 27 Feb. 0.5 kWh against 17) takes Enedis's total spread as the home usually spreads it at that
    time of the year. Days Enedis does not know stay as they were."""
    import copy
    readings = [r for r in home.readings.values() if r.meter.kind == kind]
    if not readings:
        return home
    tz = home.tz
    reference_days = {d: t.kwh for d, t in stats.days(reference, tz).items() if t.complete}
    own: dict[date, float] = {}
    for r in readings:
        for d, t in stats.days(r.series, tz).items():
            own[d] = own.get(d, 0.0) + (t.kwh if t.complete else float("nan"))

    def profile(around: date) -> dict[tuple[str, int], float]:
        """Each meter's usual share of each hour of the day, over the four weeks around `around`."""
        seen: dict[tuple[str, int], float] = {}
        for r in readings:
            for h in r.series.hours:
                local = h.start.astimezone(tz)
                if h.kwh is not None and h.hours == 1 and abs((local.date() - around).days) <= 14 and own.get(local.date(), 0) >= 1:
                    seen[(r.meter.stat, local.hour)] = seen.get((r.meter.stat, local.hour), 0.0) + h.kwh
        total = sum(seen.values())
        return {k: v / total for k, v in seen.items()} if total else {}

    new = copy.copy(home)
    new.readings = dict(home.readings)
    missed = {d for d, kwh in reference_days.items() if d in own and own[d] == own[d] and own[d] < 1 <= kwh}
    shapes = {d: profile(d) for d in missed}
    for r in readings:
        hours = []
        for h in r.series.hours:
            d = h.start.astimezone(tz).date()
            if d in missed and shapes[d]:
                continue
            if h.kwh is not None and d in reference_days and own.get(d, 0) == own.get(d, 0) and own.get(d, 0) >= 1:
                h = Hour(h.start, h.kwh * reference_days[d] / own[d], h.hours)
            hours.append(h)
        for d in missed:
            if not shapes[d]:
                continue
            for hour in range(24):
                share = shapes[d].get((r.meter.stat, hour))
                if share:
                    start = datetime.combine(d, datetime.min.time(), tz).replace(hour=hour).astimezone(timezone.utc)
                    hours.append(Hour(start, reference_days[d] * share, 1))
        hours.sort(key=lambda h: h.start)
        series = Series(r.series.stat, backs=r.series.backs, jumps=r.series.jumps)
        series.hours = hours
        new.readings[r.meter.stat] = Reading(r.meter, series, r.factor, r.lag, r.since)
    merged = stats.merge(*[new.readings[r.meter.stat].series for r in readings])
    if kind == "import":
        new.bought = merged
    else:
        new.sent = merged
    return new
