"""The reports in euros (lots 2.1, 2.2, 2.9): a day, a month, any period, with what is not known said, never guessed.

Built on `home.Home` (the meters read and checked) and `tariff.Contract`. The sun's share is said in the family's
words (PHRASES.md rule 3): « le soleil couvre {x} % de la maison », « la maison a gardé {y} % de son soleil ».
"""
from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from . import stats, tariff
from .home import Home
from .tariff import Contract


@dataclass
class Period:
    start: datetime
    end: datetime
    bought_kwh: float
    energy_eur: float | None          # None: a price was not known for some of the energy
    subscription_eur: float | None
    unknown_hours: int
    sun_kwh: float | None = None
    sent_kwh: float | None = None
    sent_eur: float | None = None

    @property
    def eur(self) -> float | None:
        if self.energy_eur is None or self.subscription_eur is None:
            return None
        return self.energy_eur + self.subscription_eur

    @property
    def used_kwh(self) -> float:
        # Without the sun measured, what was sent cannot come out of it: only what was bought is known.
        if self.sun_kwh is None:
            return self.bought_kwh
        return self.bought_kwh + self.sun_kwh - (self.sent_kwh or 0.0)

    @property
    def sun_cover(self) -> float | None:
        """The share of the home's use the sun covered."""
        if self.sun_kwh is None or self.used_kwh <= 0:
            return None
        return max(0.0, min(1.0, (self.sun_kwh - (self.sent_kwh or 0.0)) / self.used_kwh))

    @property
    def sun_kept(self) -> float | None:
        """The share of the sun the home used itself."""
        if not self.sun_kwh:
            return None
        return max(0.0, min(1.0, (self.sun_kwh - (self.sent_kwh or 0.0)) / self.sun_kwh))

    def as_dict(self) -> dict:
        r = lambda v, n=2: None if v is None else round(v, n)  # noqa: E731
        return {"debut": self.start.isoformat(), "fin": self.end.isoformat(), "kwh_achetes": r(self.bought_kwh),
                "euros": r(self.eur), "euros_energie": r(self.energy_eur), "abonnement": r(self.subscription_eur),
                "heures_inconnues": self.unknown_hours, "soleil_kwh": r(self.sun_kwh), "revendu_kwh": r(self.sent_kwh),
                "revendu_euros": r(self.sent_eur),
                "soleil_couvre": None if self.sun_cover is None else round(self.sun_cover * 100),
                "soleil_garde": None if self.sun_kept is None else round(self.sun_kept * 100)}


def period(home: Home, contract: Contract, table: dict, start: datetime, end: datetime) -> Period:
    """Everything known between two instants (start included, end excluded)."""
    tz = home.tz
    euros = tariff.cost(contract, table, tz, home.metered(), start, end,
                        contract.colors if contract.option == tariff.TEMPO else None)
    bought = stats.total(home.bought, start, end) if home.bought else stats.Total(0.0, 0, 0)
    subscription = 0.0
    cursor = start
    while cursor < end:
        share = tariff.subscription(contract, table, cursor.astimezone(tz).date())
        if share is None:
            subscription = None
            break
        following = min(end, datetime.combine(cursor.astimezone(tz).date() + timedelta(days=1), datetime.min.time(), tz))
        subscription += share * (following - cursor).total_seconds() / 86400
        cursor = following
    sun = stats.total(home.sun, start, end).kwh if home.sun else None
    sent = stats.total(home.sent, start, end).kwh if home.sent else None
    sent_eur = None if sent is None or contract.export_price is None else sent * contract.export_price
    return Period(start, end, bought.kwh, None if euros.unknown_kwh else euros.eur, subscription,
                  bought.unknown_hours, sun, sent, sent_eur)


def day(home: Home, contract: Contract, table: dict, when: date) -> Period:
    start, end = tariff.day_bounds(when, home.tz)
    return period(home, contract, table, start, end)


def month(home: Home, contract: Contract, table: dict, year: int, number: int, until: datetime | None = None) -> Period:
    start = datetime(year, number, 1, tzinfo=home.tz)
    end = datetime(year + number // 12, number % 12 + 1, 1, tzinfo=home.tz)
    return period(home, contract, table, start, min(end, until) if until else end)


def projection(so_far: Period, now: datetime) -> float | None:
    """« Au rythme actuel, le mois finira à {euros} € » (5.6): the month so far, stretched to its last day."""
    if so_far.eur is None:
        return None
    local = now.astimezone(so_far.start.tzinfo)
    elapsed = (now - so_far.start).total_seconds() / 86400
    if elapsed < 3:
        return None
    return so_far.eur * monthrange(local.year, local.month)[1] / elapsed


def periods(home: Home, contract: Contract, table: dict, start: date, end: date, step: str) -> list[Period]:
    """Day, week, month or year reports between two dates (`hestia_energy/periods`)."""
    out, cursor = [], start
    while cursor <= end:
        if step == "jour":
            following = cursor + timedelta(days=1)
        elif step == "semaine":
            following = cursor + timedelta(days=7 - cursor.weekday())
        elif step == "mois":
            following = date(cursor.year + cursor.month // 12, cursor.month % 12 + 1, 1)
        else:
            following = date(cursor.year + 1, 1, 1)
        out.append(period(home, contract, table, datetime.combine(cursor, datetime.min.time(), home.tz),
                          datetime.combine(min(following, end + timedelta(days=1)), datetime.min.time(), home.tz)))
        cursor = following
    return out


def contract_for(home: Home, kva: int | None, offpeak, prices: dict | None = None, export_price: float | None = None,
                 option: str | None = None) -> Contract:
    """The contract as the home shows it: peak and off-peak meters or learned off-peak hours → HP/HC, else Base."""
    seen = {r.meter.period for r in home.of("import")}
    if option is None:
        option = tariff.HPHC if ({"hp", "hc"} <= seen or offpeak is not None) else tariff.BASE
    return Contract(option, kva or 6, offpeak, dict(prices or {}), None, export_price,
                    self_producer=bool(home.page.exports))


# --- The reviews (2.9): yesterday, last week, last month, each against its own landmark --------------------------

# Below these gaps the comparison is not worth a word.
_WORTH = {"hier": 0.5, "semaine": 1.0, "mois": 2.0}


def reviews(home: Home, contract: Contract, table: dict, now: datetime) -> list[dict]:
    """Three short reviews in the family's words: yesterday against the same weekday a week before, last week against
    the week before it, last month against the same month a year before. Each: {id, titre, texte, euros, kwh}."""
    from . import phrases
    tz = home.tz
    today = now.astimezone(tz).date()
    yesterday = today - timedelta(days=1)
    monday = today - timedelta(days=today.weekday())
    first = today.replace(day=1)
    last_month = (first - timedelta(days=1)).replace(day=1)

    def span(a: date, b: date) -> Period:
        return period(home, contract, table, tariff.day_bounds(a, tz)[0], tariff.day_bounds(b, tz)[0])

    plan = [
        ("hier", span(yesterday, today), span(yesterday - timedelta(days=7), today - timedelta(days=7)),
         f"le {phrases.WEEKDAYS[yesterday.weekday()]} d'avant", {}),
        ("semaine", span(monday - timedelta(days=7), monday), span(monday - timedelta(days=14), monday - timedelta(days=7)),
         "la semaine d'avant", {}),
        ("mois", span(last_month, first), span(last_month.replace(year=last_month.year - 1), first.replace(year=first.year - 1)),
         f"{phrases.month_name(last_month.month)} {last_month.year - 1}", {"mois": phrases.month_name(last_month.month).capitalize()}),
    ]
    out = []
    for key, this, before, landmark, extra in plan:
        if this.bought_kwh <= 0 or this.unknown_hours > 0.1 * (this.end - this.start).total_seconds() / 3600:
            continue
        values = {"kwh": phrases.number(this.used_kwh), **extra,
                  "pourcent": None if this.sun_cover is None else round(this.sun_cover * 100)}
        if this.eur is not None and before.eur is not None and before.bought_kwh > 0 and abs(this.eur - before.eur) >= _WORTH[key]:
            values.update(ecart=phrases.euros(abs(this.eur - before.eur)), sens="plus" if this.eur > before.eur else "moins",
                          repere=landmark)
        if this.eur is not None:
            title = phrases.fill(phrases.REVIEW_TITLES[key], {**values, "euros": phrases.euros(this.eur)})
        else:
            title = phrases.fill(phrases.REVIEW_TITLES_KWH[key], values)
        out.append({"id": key, "titre": title, "texte": phrases.fill(phrases.REVIEW_TEXT, values),
                    "euros": None if this.eur is None else round(this.eur, 2), "kwh": round(this.used_kwh, 1)})
    return out


def so_far(home: Home, contract: Contract, table: dict, now: datetime) -> dict | None:
    """Today until the last whole hour of the statistics, against yesterday until the same hour (2.2):
    {euros, kwh, hier_euros, hier_kwh, jusqu_a}. Euros None when a price is unknown; None before 1 h of the day."""
    tz = home.tz
    cut = now.astimezone(tz).replace(minute=0, second=0, microsecond=0)
    start = tariff.day_bounds(cut.date(), tz)[0]
    if cut <= start:
        return None
    today = period(home, contract, table, start, cut)
    before = period(home, contract, table, start - timedelta(days=1), cut - timedelta(days=1))
    # One hour set aside (a jump, a restart) leaves the comparison fair; more would not.
    if today.unknown_hours > 1 or before.unknown_hours > 1:
        return None
    r = lambda v: None if v is None else round(v, 2)  # noqa: E731
    return {"euros": r(today.eur), "kwh": r(today.used_kwh), "hier_euros": r(before.eur), "hier_kwh": r(before.used_kwh),
            "jusqu_a": cut.isoformat()}
