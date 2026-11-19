"""« Ton contrat, bien utilisé » (Frank, 19 Nov. 2026): not « change your contract » but « use it better ».

Over the last twelve months:
- the share of the purchases in off-peak hours, against the share from which they pay ((HP − Base) ÷ (HP − HC)), and
  what the Base option would have cost: the contract is said good or not, on a year, never on one month (Frank's
  November: 19 %, his year: 33 %, threshold 28 %);
- for each device that can wait (the water heater, the washing machine, the dishwasher, the dryer), its energy taken in
  the sun, at night (off-peak) and in paid peak hours, and what moving those paid peak hours would save a year at
  today's prices. With panels the sun comes first: an hour where the home sends more than 0.3 kWh to the grid is a
  sunny hour, and a kWh used then costs only the resale it no longer brings;
- how many days of each month had sun to spare (two hours sending 1 kWh or more): enough for a machine. From March to
  October nearly every day at Frank's, from November to February nearly never: the advice of the day reads the forecast,
  never a fixed season.

Plain Python, no Home Assistant: one pass over the year's hours (about 9 000 a device), made once a day.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
import dataclasses

from . import report, tariff
from .advice import kind_of

SUN_KWH = 0.3              # an hour sending this much: the sun is in excess, a machine would run on it
SPARE_KWH = 1.0            # an hour sending this much: enough sun for a machine's cycle…
SPARE_HOURS = 2            # …during two hours at least: a day with sun to spare
MIN_DAYS = 60              # two months hour by hour at least before saying anything
MIN_KWH = 5.0              # a device that used less in a year is not worth a line
SHIFTABLE = ("chauffe_eau", "machine")
YEAR = timedelta(days=365)


def _hour_floor(at: datetime) -> datetime:
    return at.replace(minute=0, second=0, microsecond=0)


def usage(home, contract, table, now: datetime, names: dict | None = None) -> dict | None:
    """The year of the contract and of the devices that can wait, or None (not on peak / off-peak hours, too few days)."""
    if contract.option != tariff.HPHC or contract.offpeak is None or home.bought is None:
        return None
    tz = home.tz
    end = _hour_floor(now)
    start = end - YEAR
    hp = tariff.price_at(contract, table, now, tz, tariff.HP)
    hc = tariff.price_at(contract, table, now, tz, tariff.HC)
    if hp is None or hc is None or hp <= hc:
        return None

    def offpeak(at: datetime) -> bool:
        return contract.offpeak.contains(at + timedelta(minutes=30), tz)

    # The purchases: by each meter's own period, else by the off-peak hours.
    bought = {tariff.HP: 0.0, tariff.HC: 0.0}
    days: set[date] = set()
    for series, period in home.metered():
        for hour in series.between(start, end):
            if hour.kwh is None:
                continue
            if period in bought:
                bought[period] += hour.kwh
            elif hour.hours == 1:
                bought[tariff.HC if offpeak(hour.start) else tariff.HP] += hour.kwh
            else:
                continue
            days.add(hour.start.astimezone(tz).date())
    total = bought[tariff.HP] + bought[tariff.HC]
    if total <= 0 or len(days) < MIN_DAYS:
        return None
    share = bought[tariff.HC] / total

    # The sunny hours, and each month's days with sun to spare.
    sunny: set[datetime] = set()
    spare: dict[date, int] = {}
    if home.sent is not None:
        for hour in home.sent.between(start, end):
            if hour.kwh is None or hour.hours != 1:
                continue
            if hour.kwh > SUN_KWH:
                sunny.add(hour.start)
            if hour.kwh >= SPARE_KWH:
                day = hour.start.astimezone(tz).date()
                spare[day] = spare.get(day, 0) + 1
    months = _sun_months(spare, days) if home.sent is not None else []

    devices = []
    for reading in home.of("device"):
        if reading.meter.included_in:
            continue
        name = reading.meter.name or (names or {}).get(reading.meter.stat) or reading.meter.stat
        kind = kind_of(name, reading.meter.stat)
        if kind not in SHIFTABLE:
            continue
        sun = night = peak = 0.0
        for hour in reading.series.between(start, end):
            if hour.kwh is None or hour.kwh <= 0 or hour.hours != 1:
                continue
            if hour.start in sunny:
                sun += hour.kwh
            elif offpeak(hour.start):
                night += hour.kwh
            else:
                peak += hour.kwh
        used = sun + night + peak
        if used < MIN_KWH:
            continue
        devices.append({"nom": name.strip(), "type": kind, "kwh": round(used, 1), "soleil": round(sun / used, 3),
                        "nuit": round(night / used, 3), "pleines": round(peak / used, 3),
                        "pleines_kwh": round(peak, 1), "euros_an": round(peak * (hp - hc), 2)})
    devices.sort(key=lambda d: -d["euros_an"])
    heater = next((d for d in devices if d["type"] == "chauffe_eau"), None)

    # The Base option over the same year, subscriptions included.
    base_more = None
    year = report.period(home, contract, table, start, end)
    as_base = report.period(home, dataclasses.replace(contract, option=tariff.BASE, prices={}, colors={}, subscription_year=None),
                            table, start, end)
    if year.eur is not None and as_base.eur is not None:
        base_more = round(as_base.eur - year.eur, 2)
    base_price = tariff.regulated_price(table, now.astimezone(tz).date(), tariff.BASE, contract.kva)
    threshold = None if base_price is None else round(max(0.0, (hp - base_price) / (hp - hc)), 3)

    return {
        "du": start.isoformat(), "au": end.isoformat(), "jours": len(days),
        "part_hc": round(share, 3), "seuil_hc": threshold,
        # The share once the water heater's paid peak hours go to the night (the gauge's second mark).
        "part_hc_chauffe_eau": None if heater is None else round((bought[tariff.HC] + heater["pleines_kwh"]) / total, 3),
        "base_de_plus": base_more,
        "prix": {"soleil": contract.export_price, "hc": round(hc, 4), "hp": round(hp, 4)},
        "appareils": devices,
        "euros_an": round(sum(d["euros_an"] for d in devices), 2),
        "soleil_mois": months,
    }


def _sun_months(spare: dict[date, int], days: set[date]) -> list[dict]:
    """Each month known: how many of its days had sun to spare for a machine."""
    out: dict[tuple[int, int], list[int]] = {}
    for day in days:
        key = (day.year, day.month)
        counted = out.setdefault(key, [0, 0])
        counted[1] += 1
        if spare.get(day, 0) >= SPARE_HOURS:
            counted[0] += 1
    return [{"mois": f"{y:04d}-{m:02d}", "jours": n, "sur": of} for (y, m), (n, of) in sorted(out.items())]


def heater_gain(found: dict | None) -> float | None:
    """What the water heater's paid peak hours cost more than the night, a year (the banner's figure)."""
    if not found:
        return None
    heater = next((d for d in found.get("appareils", []) if d["type"] == "chauffe_eau"), None)
    return None if heater is None else heater["euros_an"]

