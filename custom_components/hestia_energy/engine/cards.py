"""What the detail cards need beyond the reports (maquette des cartes 2, INTERFACE.md § 4.2): one period per card.

Soleil = today · Appareils = today · Pointe = today · Eau = this month · Contrat = this month · Veille = the last
nights · Chauffage = the season (from 1 October). Pure Python: the home's series come in, plain dicts go out (French
keys, rounded, None when unknown, never a guessed value).
"""
from __future__ import annotations

from calendar import monthrange
import dataclasses
from datetime import date, datetime, timedelta, tzinfo

from . import baseline, heating, report, solar, sources, stats, tariff
from .home import Home
from .rows import when
from .tariff import Contract

QUIET_SHARE = 0.2     # « quand tout dort »: the quietest fifth of the night hours of the window
QUIET_MIN_HOURS = 10
DEVICE_MIN_W = 2      # a device under this at night is not worth a line


def _name(reading, names: dict | None) -> str:
    """A device's name in the page, else its entity's own name (never « sensor.salon_prise_tv »)."""
    return reading.meter.name or (names or {}).get(reading.meter.stat) or reading.meter.stat


def _r(value: float | None, n: int = 2) -> float | None:
    return None if value is None else round(value, n)


# --- Soleil · aujourd'hui ---------------------------------------------------------------------------------------

def sun_today(hours: list[dict]) -> dict | None:
    """The hour the sun gave most today (« entre 11 h et midi : 1,4 kWh »)."""
    best = max((h for h in hours if h.get("soleil")), key=lambda h: h["soleil"], default=None)
    return None if best is None else {"h": best["h"], "kwh": best["soleil"]}


def panel_groups(channel_rows: dict[str, list[dict]], names: dict[str, str], tz: tzinfo, day: date) -> list[dict]:
    """Each group of panels (an inverter's channels: « Sud · voie 1 » and « Sud · voie 2 » → « Sud ») today, in kWh
    from each channel's hourly mean power; the biggest first."""
    out: dict[str, float] = {}
    for channel, rows in channel_rows.items():
        group = (names.get(channel) or channel).split(" · ")[0]
        for start, mean in solar._means(rows):
            if when(start).astimezone(tz).date() != day:
                continue
            out[group] = out.get(group, 0.0) + max(0.0, mean) / 1000
    return [{"nom": n, "kwh": round(k, 2)} for n, k in sorted(out.items(), key=lambda x: -x[1])]


# --- Chauffage · depuis le 1er octobre --------------------------------------------------------------------------

def season_start(today: date) -> date:
    """The heating season starts on 1 October (Suivi Stock Pellet's own season)."""
    return date(today.year if today.month >= 10 else today.year - 1, 10, 1)


def stove_stock(stock_kg: float | None, season_kg: float | None, days_used: float | None, first: date, today: date) -> dict | None:
    """The pellets left, and how many days of stove they make at this season's pace."""
    if stock_kg is None:
        return None
    days = days_used if days_used and days_used > 0 else (today - first).days + 1
    per_day = season_kg / days if season_kg and days else None
    return {"stock_kg": _r(stock_kg, 1), "jours_restants": None if not per_day else round(stock_kg / per_day)}


def gas_season(readings: list, units: dict[str, str | None], prices: dict[str, float], cold: dict[date, float],
               no_cold: str | None, now: datetime) -> dict | None:
    """The gas meters of the page, this month and this season: all that was burnt and, when the cold of each day is
    known, the heating in it — the radiators' line (engine/heating.py), drawn through the gas of each day, says what
    the home burns without heating; the rest of the gas is the heating.

    `units`: each meter's unit (« kWh » or « m³ »); `prices`: its price now, per unit; `no_cold`: why the cold is not
    known (the state then shown), or None; `now`: local. None without a meter whose unit is known, when the meters
    do not count in the same unit (kWh and m³ are never added up), or when nothing was counted this season."""
    readings = [r for r in readings if units.get(r.meter.stat)]
    if len({units[r.meter.stat] for r in readings}) != 1:
        return None
    unit = units[readings[0].meter.stat]
    scale = 0.001 if unit == sources.GAS_VOLUME else 1.0     # volumes are read in litres
    tz, today = now.tzinfo, now.date()
    burnt: dict[date, float] = {}
    counted: dict[date, int] = {}
    gaps: set[date] = set()
    since: list[date] = []     # each meter's first day: before it, the meter was not there, and nothing is missing
    for reading in readings:
        days = stats.days(reading.series, tz)
        since.append(min(days, default=today))
        for day, t in days.items():
            burnt[day] = burnt.get(day, 0.0) + t.kwh * scale
            counted[day] = counted.get(day, 0) + 1
            if not t.complete:
                gaps.add(day)
    first = season_start(today)
    # One price for the euros: the season's own average over the meters, each at its price; none when a meter has none.
    price = None
    if all(prices.get(r.meter.stat) is not None for r in readings):
        start = datetime.combine(first, datetime.min.time(), tz)
        each = {r.meter.stat: stats.total(r.series, start, now).kwh * scale for r in readings}
        whole = sum(each.values())
        price = sum(q * prices[stat] for stat, q in each.items()) / whole if whole > 0 else prices[readings[0].meter.stat]
    # The line is learned on the whole days every meter there counted: not today, not a day with a gap.
    known = {d: v for d, v in burnt.items() if d < today and d not in gaps and counted[d] == sum(1 for s in since if s <= d)}
    learned = None if no_cold else heating.learn(known, cold, heating.GAS_SPAN)
    rest = heating.without_heating(known, cold, learned)
    season = heating.gas_over(burnt, rest, first, today, price)
    if season is None:
        return None
    month = heating.gas_over(burnt, rest, today.replace(day=1), today, price)
    state = no_cold or ("apprend" if learned is None else "pret" if learned.reliable else "peu_lie")
    out = {"etat": state, "unite": unit, "prix": _r(price, 4), "mois": None if month is None else month.as_dict(),
           "saison": {**season.as_dict(), "du": first.isoformat()}}
    if state == "apprend":
        out["jours"] = sum(1 for d in known if d in cold)
    elif state == "pret":
        out.update({"par_degre": _r(learned.per_degree_kwh, 3), "reste_par_jour": _r(rest, 2),
                    "euros_par_degre": None if price is None else _r(learned.per_degree_kwh * price, 3)})
    return out


# --- Veille · les dernières nuits -------------------------------------------------------------------------------

def night_devices(home: Home, end: date, baseload_w: float | None, price: float | None, names: dict | None = None) -> dict | None:
    """What each measured device draws when the home is at its quietest at night (the quietest fifth of the night
    hours of the last 28 nights, those the baseload is read on), and what is left « sans prise mesurée »."""
    if home.bought is None:
        return None
    tz = home.tz
    first = end - timedelta(days=baseline.WINDOW_DAYS)
    night = {}
    for hour in home.bought.hours:
        local = hour.start.astimezone(tz)
        if hour.kwh is not None and hour.hours == 1 and baseline.NIGHT[0] <= local.hour < baseline.NIGHT[1] and first < local.date() <= end:
            night[hour.start] = hour.kwh
    if len(night) < QUIET_MIN_HOURS:
        return None
    quiet = sorted(night, key=night.get)[:max(QUIET_MIN_HOURS, int(len(night) * QUIET_SHARE))]
    rows = []
    for reading in home.of("device"):
        if reading.meter.included_in:
            continue
        values = {h.start: h.kwh for h in reading.series.hours if h.kwh is not None and h.hours == 1}
        seen = [values[t] for t in quiet if t in values]
        if len(seen) < len(quiet) / 2:
            continue
        watts = sum(seen) / len(seen) * 1000
        if watts >= DEVICE_MIN_W:
            rows.append({"nom": _name(reading, names), "w": round(watts), "euros_par_an": _r(baseline.yearly_euros(round(watts), price), 0)})
    rows.sort(key=lambda r: -r["w"])
    measured = sum(r["w"] for r in rows)
    rest = None if baseload_w is None else baseload_w - measured
    return {"appareils": rows, "mesure_w": measured,
            "sans_prise_w": None if rest is None or rest < DEVICE_MIN_W else round(rest),
            "sans_prise_euros_par_an": None if rest is None or rest < DEVICE_MIN_W else _r(baseline.yearly_euros(round(rest), price), 0)}


def night_drift(history: list[dict], price: float | None) -> dict | None:
    """From the first night of the history to the last one: « passée de 248 W à 194 W depuis le 10 octobre »."""
    if len(history) < 2:
        return None
    first, last = history[0], history[-1]
    gap = last["w"] - first["w"]
    return {"debut_w": first["w"], "debut": first["jour"], "ecart_w": gap,
            "ecart_euros_par_an": _r(baseline.yearly_euros(gap, price), 0)}


# --- Eau · ce mois-ci -------------------------------------------------------------------------------------------

def water_days(series: stats.Series, tz: tzinfo, now: datetime, price_m3: float | None) -> dict:
    """Each day of the month in litres, the biggest one and its cost, the average litres a day."""
    local = now.astimezone(tz)
    first = local.date().replace(day=1)
    days = stats.days(series, tz)
    out = []
    day = first
    while day <= local.date():
        t = days.get(day)
        out.append({"jour": day.isoformat(), "l": None if t is None else round(t.kwh)})
        day += timedelta(days=1)
    known = [d for d in out if d["l"] is not None]
    biggest = max(known, key=lambda d: d["l"], default=None)
    whole = [d["l"] for d in known if d["jour"] != local.date().isoformat()]
    euros = (lambda l: None if price_m3 is None else round(l / 1000 * price_m3, 2))  # noqa: E731
    return {"jours": out,
            "plus_gros": None if biggest is None else {**biggest, "euros": euros(biggest["l"])},
            "l_par_jour": round(sum(whole) / len(whole)) if whole else None,
            "euros_100_l": None if price_m3 is None else round(price_m3 / 10, 2)}


# --- Appareils · aujourd'hui ------------------------------------------------------------------------------------

def devices_today(home: Home, today: report.Period, names: dict | None = None) -> dict | None:
    """Each measured device since midnight, in kWh and in euros at the day's average price of a kWh used (the sun
    shared out equally: what was bought costs, the sun kept costs nothing); and what no plug measures."""
    devices = [r for r in home.of("device") if not r.meter.included_in]
    if not devices:
        return None
    used = today.used_kwh
    price = today.energy_eur / used if today.energy_eur is not None and used > 0 else None
    rows = []
    for reading in devices:
        total = stats.total(reading.series, today.start, today.end)
        if total.kwh > 0.005:
            rows.append({"nom": _name(reading, names), "kwh": round(total.kwh, 2),
                         "euros": None if price is None else round(total.kwh * price, 2)})
    rows.sort(key=lambda r: -r["kwh"])
    measured = sum(r["kwh"] for r in rows)
    return {"appareils": rows, "mesure_kwh": round(measured, 2), "maison_kwh": round(used, 2),
            "sans_prise_kwh": round(used - measured, 2) if used - measured >= 0.05 else None,
            "prix_moyen": _r(price, 4)}


# --- Pointe · aujourd'hui ---------------------------------------------------------------------------------------

def peak_today(hours: list[dict], kva: float | None) -> dict | None:
    """The busiest hour bought from the grid today (an hour's mean, in kW) and its share of the subscribed power."""
    best = max((h for h in hours if h.get("achat") is not None), key=lambda h: h["achat"], default=None)
    if best is None:
        return None
    return {"h": best["h"], "kw": best["achat"], "part": None if not kva else round(best["achat"] / kva, 3)}


# --- Contrat · ce mois-ci ---------------------------------------------------------------------------------------

def contract_month(home: Home, contract: Contract, table: dict, now: datetime, month: report.Period) -> dict:
    """The prices now, the subscription a month, the share of this month's purchases in off-peak hours, what the Base
    option would have cost this month, and the share from which off-peak hours pay off ((HP − Base) ÷ (HP − HC))."""
    tz = home.tz
    local = now.astimezone(tz)
    today = local.date()
    out: dict = {"prix_hp": None, "prix_hc": None, "prix_base": None, "abonnement_mois": None,
                 "part_hc": None, "base_euros": None, "seuil_hc": None}
    per_day = tariff.subscription(contract, table, today)
    if per_day is not None:
        out["abonnement_mois"] = round(per_day * monthrange(today.year, today.month)[1], 2)
    base_price = contract.prices.get(tariff.BASE) if contract.option == tariff.BASE else None
    base_price = base_price or tariff.regulated_price(table, today, tariff.BASE, contract.kva)
    out["prix_base"] = _r(base_price, 4)
    if contract.option != tariff.HPHC:
        return out
    hp = tariff.price_at(contract, table, now, tz, tariff.HP)
    hc = tariff.price_at(contract, table, now, tz, tariff.HC)
    out["prix_hp"], out["prix_hc"] = _r(hp, 4), _r(hc, 4)
    # This month's purchases in off-peak hours: by the meter's own period, else by the learned hours.
    kwh = {tariff.HP: 0.0, tariff.HC: 0.0}
    for series, period in home.metered():
        for hour in series.hours:
            if not (month.start <= hour.start < month.end) or hour.kwh is None:
                continue
            if period in kwh:
                kwh[period] += hour.kwh
            elif contract.offpeak is not None and hour.hours == 1:
                kwh[tariff.HC if contract.offpeak.contains(hour.start, tz) else tariff.HP] += hour.kwh
    total = kwh[tariff.HP] + kwh[tariff.HC]
    if total > 0:
        out["part_hc"] = round(kwh[tariff.HC] / total, 3)
    if base_price is not None:
        base = report.period(home, dataclasses.replace(contract, option=tariff.BASE, prices={}, colors={}, subscription_year=None), table, month.start, month.end)
        out["base_euros"] = _r(base.eur)
        if hp is not None and hc is not None and hp > hc:
            out["seuil_hc"] = round(max(0.0, (hp - base_price) / (hp - hc)), 3)
    return out
