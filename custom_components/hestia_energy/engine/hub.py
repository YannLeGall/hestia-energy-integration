"""The Énergie tab of the Hestia-FB hub (docs/maquette-hub-energie.html, INTERFACE.md § 5): what the household reads
there, built from the engine's own figures. Plain Python, no Home Assistant import: replayed on real data in the tests.

- the devices in four groups by use, guessed from their name and changed by the household (H5);
- each device's kWh and euros last month (H4), at the month's average price of a kWh used, the sun shared out;
- each finding attached to the source or device it is about (H6).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from . import advice, report, stats
from .home import Home

# The four groups of the Appareils page (H5), in this order when their totals are equal.
GROUPS = ("chauffage", "eau_chaude", "cuisine_linge", "reste")
GROUP_NAMES = {"chauffage": "Chauffage", "eau_chaude": "Eau chaude", "cuisine_linge": "Cuisine et linge", "reste": "Le reste"}
_GROUP_OF_KIND = {"chauffage": "chauffage", "seche_serviettes": "chauffage", "chauffe_eau": "eau_chaude",
                  "machine": "cuisine_linge", "cuisson": "cuisine_linge", "froid": "cuisine_linge"}


def guess_group(name: str | None, stat: str = "") -> str:
    """The group a device goes in by its name (« Chauffe-eau » → Eau chaude), « Le reste » when nothing says."""
    return _GROUP_OF_KIND.get(advice.kind_of(name, stat), "reste")


def device_id(stat: str) -> str:
    """The device's address in the tab (« sensor.chauffe_eau_total_energy » → « chauffe_eau_total_energy »)."""
    return stat.split(".", 1)[-1].replace(":", "_")


def last_month(now: datetime, tz) -> tuple[int, int]:
    local = now.astimezone(tz)
    first = local.date().replace(day=1) - timedelta(days=1)
    return first.year, first.month


def devices_month(home: Home, period: report.Period) -> dict | None:
    """Each measured device over a month: kWh, and euros at that month's average price of a kWh used (what was bought
    costs, the sun kept costs nothing). Sub-meters are listed but counted once in the share of the home measured."""
    devices = home.of("device")
    if not devices:
        return None
    used = period.used_kwh
    price = period.energy_eur / used if period.energy_eur is not None and used > 0 else None
    out, measured = {}, 0.0
    for reading in devices:
        total = stats.total(reading.series, period.start, period.end)
        kwh = round(total.kwh, 2) if total.hours else None
        out[reading.meter.stat] = {"kwh": kwh, "euros": None if kwh is None or price is None else round(kwh * price, 2)}
        if kwh and not reading.meter.included_in:
            measured += kwh
    return {"debut": period.start.date().isoformat(), "prix_moyen": None if price is None else round(price, 4),
            "maison_kwh": round(used, 1), "mesure_kwh": round(measured, 1),
            "part": round(measured / used * 100) if used > 0 else None, "appareils": out}


def twelve_months(home: Home, contract, table: dict, now: datetime) -> dict | None:
    """The last twelve whole months, subscription included (the overview's figure without panels, H2)."""
    local = now.astimezone(home.tz)
    end = datetime(local.year, local.month, 1, tzinfo=home.tz)
    start = datetime(local.year - 1, local.month, 1, tzinfo=home.tz)
    whole = report.period(home, contract, table, start, end)
    if whole.bought_kwh <= 0:
        return None
    return {"euros": None if whole.eur is None else round(whole.eur, 2), "kwh": round(whole.used_kwh),
            "du": start.date().isoformat(), "au": (end - timedelta(days=1)).date().isoformat(),
            "soleil_couvre": None if whole.sun_cover is None else round(whole.sun_cover * 100),
            "revendu_euros": None if whole.sent_eur is None else round(whole.sent_eur, 2)}


# --- The findings, each where it belongs (H6) -------------------------------------------------------------------

def owner(finding: dict, page) -> str | None:
    """The statistic of the page's meter a finding is about: its own, or the meter whose live power it is."""
    stat = finding.get("stat") or ""
    if not stat:
        return None
    for meter in page.meters:
        if stat == meter.stat or stat in meter.power.entities:
            return meter.stat
    return stat


def by_meter(findings: list[dict], page) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for f in findings:
        key = owner(f, page)
        if key:
            out.setdefault(key, []).append(f)
    return out


def enedis_lines(findings: list[dict], what: str) -> list[dict]:
    """« Comparé à Enedis » for one source (« vos achats », « votre revente »): the gap, then the days far off."""
    from . import phrases
    lines = []
    for f in findings:
        v = f.get("valeurs") or {}
        if v.get("quoi") != what:
            continue
        if f["id"] == "p_reference_ecart":
            lines.append({"titre": f"Enedis compte {v['pourcent']} % de {v['sens']} que vos compteurs",
                          "texte": f"Sur {phrases.number(v['jours'])} jours. Vos euros suivent Enedis."})
        elif f["id"] == "p_reference_jours":
            day = date.fromisoformat(v["date"]) if isinstance(v.get("date"), str) else v.get("date")
            when = f"{day.day} {phrases.month_name(day.month)} {day.year}" if day else ""
            n = v["jours"]
            page, enedis = v["page"], v["enedis"]
            lines.append({"titre": f"{n} jour{'s' if n > 1 else ''} nettement différent{'s' if n > 1 else ''}",
                          "texte": f"Dont le {when} : {phrases.number(page, 1 if page < 10 else 0)} kWh contre "
                                   f"{phrases.number(enedis, 1 if enedis < 10 else 0)}."})
    return lines
