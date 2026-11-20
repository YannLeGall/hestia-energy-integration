"""« Ton contrat, bien utilisé » (Frank, 19 Nov. 2026): not « change your contract » but « use it better ».

Over the last twelve months:
- the share of the purchases in off-peak hours, against the share from which they pay ((HP − Base) ÷ (HP − HC)), and
  what the Base option would have cost: the contract is said good or not, on a year, never on one month (Frank's
  November: 19 %, his year: 33 %, threshold 28 %);
- for each device that can wait (the water heater, the washing machine, the dishwasher, the dryer), its energy taken in
  the sun, at night (off-peak) and in paid peak hours, and what moving those paid peak hours would save a year at
  today's prices. With panels the sun comes first: a kWh used in the sun costs only the resale it no longer brings.
  The sun a device used is the surplus there would have been without it (sent + its own use − bought, at most its
  own use): a water heater of 2.2 kW eats a 1.5 kW surplus whole, and the home then sends nothing (Frank's summer:
  the heater's sunny noons were counted as peak hours);
- its cycles (a run of hours above 0.2 kWh): how many, at what hour they start, how many in paid peak hours, and,
  for a water heater with panels, the months the sun does not reach it (Frank's: November to February, set at 11 h);
- how many days of each month had sun to spare (two hours sending 1 kWh or more): enough for a machine. From March to
  October nearly every day at Frank's, from November to February nearly never: the advice of the day reads the forecast,
  never a fixed season.

Plain Python, no Home Assistant: one pass over the year's hours (about 9 000 a device), made once a day.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
import dataclasses

from . import phrases, report, tariff
from .advice import kind_of
from .rows import Rows

SUN_KWH = 0.3              # an hour sending this much: the sun is in excess (the old rule, kept when bought is unknown)
CYCLE_KWH = 0.2            # an hour above this: the device runs…
CALM_HOURS = 2             # …and a cycle ends after two hours below it
RECENT = timedelta(days=60)  # the hour a device starts now: its last two months (Frank moved the heater 12 h → 11 h)
DARK_SHARE = 0.2           # a month where the water heater takes less than this in the sun: the sun does not reach it
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

    # Each hour's purchases and resale, for the sun a device used (its own use put back into the surplus).
    grid: dict[datetime, float] = {}
    sent: dict[datetime, float] = {}
    if home.sent is not None:
        sent = {h.start: h.kwh for h in home.sent.between(start, end) if h.kwh is not None and h.hours == 1}
        if home.bought is not None:
            grid = {h.start: h.kwh for h in home.bought.between(start, end) if h.kwh is not None and h.hours == 1}

    devices = []
    for reading in home.of("device"):
        if reading.meter.included_in:
            continue
        name = reading.meter.name or (names or {}).get(reading.meter.stat) or reading.meter.stat
        kind = kind_of(name, reading.meter.stat)
        if kind not in SHIFTABLE:
            continue
        found = _device(reading.series.between(start, end), sent, grid, sunny, offpeak, tz, end, home.sent is not None)
        if found is None:
            continue
        sun, night, peak = found.pop("_split")
        used = sun + night + peak
        devices.append({"nom": name.strip(), "type": kind, "kwh": round(used, 1), "soleil": round(sun / used, 3),
                        "nuit": round(night / used, 3), "pleines": round(peak / used, 3),
                        "pleines_kwh": round(peak, 1), "euros_an": round(peak * (hp - hc), 2), **found})
        dark = found.get("mois_sans_soleil")
        if dark:
            devices[-1]["euros_sans_soleil"] = round(found["pleines_sans_soleil_kwh"] * (hp - hc), 2)
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
        # The hours the sun is usually to spare, on the days it is (« entre 11 h et 16 h »).
        "soleil_heures": _sun_hours(home.sent.between(start, end), tz) if home.sent is not None else None,
    }


def _device(hours, sent: dict, grid: dict, sunny: set, offpeak, tz, end: datetime, panels: bool) -> dict | None:
    """One device's year: its split (sun, night, peak), its hours of the day, its cycles and its months."""
    sun = night = peak = 0.0
    by_hour = [[0.0, 0.0, 0.0] for _ in range(24)]
    by_month: dict[int, list[float]] = {}
    days_of_month: dict[int, set] = {}
    cycles: list[dict] = []
    run: dict | None = None
    calm = 0
    last: datetime | None = None
    for hour in hours:
        if hour.kwh is None or hour.hours != 1:
            continue
        local = hour.start.astimezone(tz)
        days_of_month.setdefault(local.month, set()).add(local.date())
        kwh = max(0.0, hour.kwh)
        if kwh > 0:
            bought = grid.get(hour.start)
            if bought is not None:
                part_sun = min(kwh, max(0.0, sent.get(hour.start, 0.0) + kwh - bought))
            else:
                part_sun = kwh if hour.start in sunny else 0.0
            rest = kwh - part_sun
            hc = offpeak(hour.start)
            split = (part_sun, rest if hc else 0.0, 0.0 if hc else rest)
            sun, night, peak = sun + split[0], night + split[1], peak + split[2]
            for i in range(3):
                by_hour[local.hour][i] += split[i]
            month = by_month.setdefault(local.month, [0.0, 0.0, 0.0])
            for i in range(3):
                month[i] += split[i]
        else:
            split = (0.0, 0.0, 0.0)
        # A gap in the statistics ends a cycle too.
        if run is not None and last is not None and hour.start - last > timedelta(hours=1):
            cycles.append(run)
            run, calm = None, 0
        last = hour.start
        if kwh > CYCLE_KWH:
            if run is None:
                run = {"start": local, "hc": offpeak(hour.start), "kwh": 0.0, "peak": 0.0, "hours": 0}
            run["kwh"] += kwh
            run["peak"] += split[2]
            run["hours"] += 1 + calm
            calm = 0
        elif run is not None:
            calm += 1
            run["kwh"] += kwh
            run["peak"] += split[2]
            if calm >= CALM_HOURS:
                cycles.append(run)
                run, calm = None, 0
    if run is not None:
        cycles.append(run)
    used = sun + night + peak
    if used < MIN_KWH:
        return None
    out: dict = {"_split": (sun, night, peak),
                 "profil": [[round(v / used, 3) for v in h] for h in by_hour]}
    if cycles:
        recent = [c for c in cycles if c["start"] >= end.astimezone(tz) - RECENT]
        chosen = recent if len(recent) >= 5 else cycles
        hour_of, share = _mode([c["start"].hour for c in chosen])
        at_night = [c for c in cycles if c["hc"]]
        starts_day = [c["start"].hour for c in cycles if not c["hc"]]
        spread = [h for h in range(24) if starts_day.count(h) >= max(1, 0.03 * len(cycles))]
        out.update({"cycles": len(cycles), "kwh_cycle": round(sum(c["kwh"] for c in cycles) / len(cycles), 2),
                    "duree": max(1, round(sum(c["hours"] for c in cycles) / len(cycles))),
                    "depart": hour_of, "depart_part": round(share, 3),
                    "prix_fort": round(sum(1 for c in cycles if c["peak"] >= c["kwh"] / 2) / len(cycles), 3),
                    "en_differe": round(len(at_night) / len(cycles), 3),
                    "depart_nuit": _mode([c["start"].hour for c in at_night])[0] if at_night else None,
                    "plage": [min(spread), max(spread) + 1] if spread else None})
    if panels:
        dark = sorted(m for m, v in by_month.items() if sum(v) >= 1 and v[0] / sum(v) < DARK_SHARE)
        if dark and len(dark) < len(by_month):
            out["mois_sans_soleil"] = dark
            out["pleines_sans_soleil_kwh"] = round(sum(by_month[m][2] for m in dark), 1)
            out["jours_sans_soleil"] = sum(len(days_of_month.get(m, ())) for m in dark)
    return out


def _mode(values: list[int]) -> tuple[int | None, float]:
    """The most frequent value and its share."""
    if not values:
        return None, 0.0
    best = max(set(values), key=lambda v: (values.count(v), -v))
    return best, values.count(best) / len(values)


def _sun_hours(hours, tz) -> list[int] | None:
    """On the days with sun to spare, the hours that send 1 kWh or more one day in two: [first, last + 1]."""
    by_day: dict[date, set[int]] = {}
    for hour in hours:
        if hour.kwh is not None and hour.hours == 1 and hour.kwh >= SPARE_KWH:
            local = hour.start.astimezone(tz)
            by_day.setdefault(local.date(), set()).add(local.hour)
    days = [h for h in by_day.values() if len(h) >= SPARE_HOURS]
    if not days:
        return None
    usual = [h for h in range(24) if sum(1 for d in days if h in d) >= len(days) / 2]
    return [min(usual), max(usual) + 1] if usual else None


# « Ce qui se fait, ce qui serait mieux, ce que ça rapporte » (Frank, 19 Nov. 2026, maquette D): one advice a device.
MIN_EUROS = 1.0
_WORDS = {"seche": ("séchage", "séchages"), "sèche": ("séchage", "séchages"), "lave": ("lavage", "lavages")}


def _words(name: str) -> tuple[str, str]:
    low = name.lower()
    for key, words in _WORDS.items():
        if key in low:
            return words
    return "cycle", "cycles"


def _night_start(contract) -> int | None:
    """The minute to start a delayed run: the longest off-peak range's start, up to the next half hour (0 h 13 → 0 h 30)."""
    if contract.offpeak is None or not contract.offpeak.ranges:
        return None
    start = max(contract.offpeak.ranges, key=lambda r: r.minutes).start
    return (start + 29) // 30 * 30 % 1440


def _from(month: str, capital: bool = False) -> str:
    """« de novembre », « d'octobre »."""
    word = "d'" if month[0] in "aeiouéèâ" else "de "
    return (word.capitalize() if capital else word) + month


def _months(numbers: list[int]) -> tuple[int, int] | None:
    """The first and last month of one run of months, across the new year (11, 12, 1, 2 → 11, 2), else None."""
    wanted = set(numbers)
    firsts = [m for m in wanted if (m - 2) % 12 + 1 not in wanted]
    if len(firsts) != 1:
        return None
    first = last = firsts[0]
    while last % 12 + 1 in wanted and last % 12 + 1 != first:
        last = last % 12 + 1
    return first, last


def advices(found: dict | None, contract, sun: bool) -> list[dict]:
    """The water heater and each machine as « Pour économiser » says them: today, better, the euros a year."""
    if not found:
        return []
    start = _night_start(contract)
    if start is None:
        return []
    at = tariff.clock(start)
    gap = found["prix"]["hp"] - found["prix"]["hc"]
    window = found.get("soleil_heures") if sun else None
    out = []
    for d in found["appareils"]:
        if d.get("cycles") is None:
            continue
        night_hours = [start // 60, start // 60 + d["duree"]]
        if d["type"] == "chauffe_eau":
            item = _heater(d, at, night_hours, gap)
        else:
            item = _machine(d, at, night_hours, window, gap)
        if item is not None:
            # The two clock times the card pins on its strips (Frank, 20 Nov.: « on ne sait pas quand il tourne et à
            # quelle heure le faire tourner »): when it starts today, when to start it.
            # A machine that runs at any hour has no start time worth a pin.
            if d["type"] == "chauffe_eau":
                first = d["depart"]
            elif d["en_differe"] >= 0.4 and d.get("depart_nuit") is not None:
                first = d["depart_nuit"]
            else:
                first = d["depart"] if d["depart_part"] >= 0.15 else None
            out.append({"rubrique": "contrat", "unite": "par an", "profil": d["profil"],
                        "depart": first * 60 if first is not None else None, "lancer": start, **item})
    return out


def _heater(d: dict, at: str, night_hours: list[int], gap: float) -> dict | None:
    if d["pleines"] < 0.1 or d["euros_an"] < MIN_EUROS:
        return None
    hour = tariff.clock(d["depart"] * 60)
    fixed = d["depart_part"] >= 0.6
    now = f"Programmé à {hour} tous les jours." if fixed else f"Il chauffe surtout vers {hour}."
    dark = d.get("mois_sans_soleil")
    run = _months(dark) if dark else None
    if run and d.get("euros_sans_soleil", 0) >= MIN_EUROS and d.get("jours_sans_soleil"):
        first, last = (phrases.month_name(m) for m in run)
        per_day = d["pleines_sans_soleil_kwh"] / d["jours_sans_soleil"]
        euros = d["euros_sans_soleil"]
        back = phrases.month_name(run[1] % 12 + 1)
        now += (f" {_from(first, True)} à {last}, il n'y a pas de soleil à cette heure-là : il prend "
                f"{phrases.number(per_day, 1 if per_day < 10 else 0)} kWh par jour au prix fort.")
        better = f"{_from(first, True)} à {last}, programmez-le à {at}. Remettez {hour} en {back} : le soleil le chauffera."
        title = f"Programmez le chauffe-eau à {at} {_from(first)} à {last}"
        under = f"par an, {phrases.euros(euros / d['jours_sans_soleil'])} € par jour sans soleil"
    else:
        euros = d["euros_an"]
        now += f" {round(d['pleines'] * 100)} % de son énergie est payée au prix fort : {phrases.number(d['pleines_kwh'])} kWh par an."
        better = f"Programmez-le à {at}, en heures creuses."
        title = f"Programmez le chauffe-eau à {at}"
        under = "par an"
    return {"id": "chauffe_eau_heures", "nom": d["nom"], "titre": title, "pourquoi": now, "maintenant": now,
            "mieux": better, "euros_an": round(euros), "sous": under, "mieux_heures": [[*night_hours, "hc"]]}


def _machine(d: dict, at: str, night_hours: list[int], window: list[int] | None, gap: float) -> dict | None:
    tenths = round(d["prix_fort"] * 10)
    if d["euros_an"] < MIN_EUROS or tenths == 0:
        return None
    one, many = _words(d["nom"])
    dear = f"tous les {many} au prix fort" if tenths == 10 else f"{tenths} {many if tenths > 1 else one} sur 10 au prix fort"
    sunny = f"entre {tariff.clock(window[0] * 60)} et {tariff.clock(window[1] * 60)}" if window else None
    if d["en_differe"] >= 0.4 and d.get("depart_nuit") is not None:
        now = f"Souvent déjà en départ différé, vers {tariff.clock(d['depart_nuit'] * 60)} : bien. Encore {dear}."
        better = f"Le départ différé pour tous les {many}" + (", sauf les jours de soleil." if sunny else ".")
    else:
        if d["depart_part"] >= 0.15:
            now = f"Il tourne surtout vers {tariff.clock(d['depart'] * 60)} : {dear}."
        elif d.get("plage"):
            a, b = d["plage"]
            now = f"Il tourne à toute heure, de {tariff.clock(a * 60)} à {tariff.clock(b * 60)} : {dear}."
        else:
            now = f"Il tourne à toute heure : {dear}."
        better = (f"Les jours de soleil, lancez-le {sunny}. Sinon, départ différé à {at}." if sunny
                  else f"Départ différé à {at}.")
    cents = round(d["kwh_cycle"] * gap * 100)
    hours = [[*night_hours, "hc"]] + ([[*window, "soleil"]] if sunny else [])
    return {"id": "machine_heures", "nom": d["nom"], "titre": f"{d['nom']} : départ différé à {at}" + (", ou au soleil" if sunny else ""),
            "pourquoi": now, "maintenant": now, "mieux": better, "euros_an": round(d["euros_an"]),
            "sous": f"par an, {cents} centime{'s' if cents > 1 else ''} par {one}" if cents >= 1 else "par an",
            "mieux_heures": hours}


KVAS = (3, 6, 9, 12, 15, 18, 24, 30, 36)
MIN_PEAK_DAYS = 90         # three months of daily peaks at least before a word on the power


def power(rows: list[tuple], contract, table, now: datetime, tz) -> dict | None:
    """Is the subscribed power the right one? Each day's highest power bought (the hourly « max » of the page's live
    grid power, the Linky cutting above its kVA), over the last twelve months, against the power just below:
    how many days went above it, and what its subscription would save a year. A reading above twice the subscribed
    power is a glitch, not a peak (prod, 30 Oct. 2026: 27 753 W on 9 kVA)."""
    kva = contract.kva
    if not kva or kva not in KVAS or KVAS.index(kva) == 0:
        return None
    since = (now - YEAR).timestamp()
    days: dict[date, float] = {}
    for found, inverted in rows:
        found = Rows.of(found) if not isinstance(found, Rows) else found
        # An inverted sensor reads the purchases below zero: its lowest is the highest bought.
        highest = found.column("min" if inverted else "max")
        if highest is None:
            continue
        for stamp, peak in zip(found.ts, highest):
            peak = -peak if inverted else peak
            if stamp < since or peak != peak or peak <= 0 or peak > 2 * kva * 1000:
                continue
            day = datetime.fromtimestamp(stamp, tz).date()
            if peak > days.get(day, 0.0):
                days[day] = peak
    if len(days) < MIN_PEAK_DAYS:
        return None
    lower = KVAS[KVAS.index(kva) - 1]
    today = now.astimezone(tz).date()
    option = contract.option if contract.option in (tariff.BASE, tariff.HPHC, tariff.TEMPO) else tariff.HPHC
    now_year = tariff.regulated_subscription(table, today, option, kva)
    lower_year = tariff.regulated_subscription(table, today, option, lower)
    return {"kva": kva, "jours": len(days), "pointe_w": round(max(days.values())),
            "plus_bas": {"kva": lower, "jours_au_dessus": sum(1 for w in days.values() if w > lower * 1000),
                         "euros_an": None if now_year is None or lower_year is None else round(now_year - lower_year, 2)}}


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

