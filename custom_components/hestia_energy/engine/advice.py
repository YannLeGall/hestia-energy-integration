"""The one advice of the banner (lots 4.1, 4.2, 4.5, 4.7): a gesture or « Rien à faire », never two.

The situations and their order are those of PHRASES.md § 2 (the first true one wins), built on the advice table
validated on 3 October for card 3 (ha-energie/README.md): a « machine » is a device that can wait, of 800 W or more —
the washing machine, the dishwasher, the dryer —, not the oven nor a radiator. Orange always speaks of next time: a
machine is never stopped mid-cycle.

`Situation` is what the home looks like now: from the live states at level 1, or from one hour of statistics in the
replay. Powers in W; a missing one is None and the situations that need it stay silent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, tzinfo
import re
import unicodedata

from . import phrases
from .tariff import clock

MACHINE_W = 800
SURPLUS_W = 1000           # « plus d'1 kW part au réseau »
SMALL_SURPLUS_W = 300
COVERED_W = 300            # bought below this while the sun shines: the sun covers the home
SUN_W = 30
BREAKER_SHARE = 0.95
HC_SOON_H = 4

# Kinds of devices, by their name in the Energy page (a household setting overrides it, lot 8.4).
_KINDS = (
    ("machine", r"lave.?linge|lave.?vaisselle|seche.?linge|washing|dishwasher|dryer|machine a laver|lavante|sechante"),
    ("chauffe_eau", r"chauffe.?eau|cumulus|ballon|ecs|water.?heater|boiler"),
    ("seche_serviettes", r"seche.?serviette|towel"),
    ("chauffage", r"chauffage|radiateur|convecteur|fil.?pilote|heater|heating|pompe a chaleur|clim"),
    ("cuisson", r"four|plaque|cuisson|oven|hob|cooktop|micro.?onde"),
    ("froid", r"frigo|refrigerateur|congelateur|fridge|freezer"),
    ("piscine", r"piscine|pool"),
)


def kind_of(name: str | None, stat: str = "") -> str:
    text = unicodedata.normalize("NFKD", f"{name or ''} {stat}").encode("ascii", "ignore").decode().lower().replace("_", " ")
    return next((kind for kind, pattern in _KINDS if re.search(pattern, text)), "autre")


@dataclass
class Running:
    name: str
    kind: str
    watts: float
    hours_on: float | None = None      # how long it has been on (for « oublié ? »)


@dataclass
class Situation:
    now: datetime
    tz: tzinfo
    period: str | None = None              # « hp », « hc », « base », None when unknown
    next_change: tuple[datetime, str] | None = None   # (instant, period that starts)
    offpeak_end: datetime | None = None
    bought_w: float | None = None
    sent_w: float | None = None
    sun_w: float | None = None
    subscribed_w: float | None = None
    running: list[Running] = field(default_factory=list)
    sun_peak: datetime | None = None       # the best hour still to come today, from the forecast (level 3)
    export_price: float | None = None
    offpeak_price: float | None = None
    water_leak_min: float | None = None
    water_litres_per_day: float | None = None
    watched: dict = field(default_factory=dict)      # device name → its normal duration in hours (« à surveiller »)

    @property
    def machines(self) -> list[Running]:
        return sorted((r for r in self.running if r.kind == "machine" and r.watts >= MACHINE_W), key=lambda r: -r.watts)

    @property
    def sunny(self) -> bool:
        return self.sun_w is not None and self.sun_w >= SUN_W


def _quarter(at: datetime, tz: tzinfo) -> str:
    """« 13 h 15 »: hours said to the quarter (PHRASES.md rule 7)."""
    local = at.astimezone(tz)
    return clock(round((local.hour * 60 + local.minute) / 15) * 15)


def _minute(at: datetime, tz: tzinfo) -> str:
    """A change of price, said to the minute."""
    local = at.astimezone(tz)
    return clock(local.hour * 60 + local.minute)


def _names(items: list[Running]) -> str:
    names = [r.name if i == 0 else r.name.lower() for i, r in enumerate(items)]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " et " + names[-1]


def _the(machine: Running) -> str:
    """« le lave-linge » in « Heures pleines pour le lave-linge »."""
    low = machine.name.strip().lower()
    if low.startswith(("le ", "la ", "les ", "l'", "l’")):
        return low
    if low[:1] in "aeiouyéèêh":
        return "l'" + low
    return ("la " if low.startswith(("machine", "plaque", "pompe")) else "le ") + low


def choose(s: Situation) -> dict:
    """The banner: {id, couleur, pastille, titre, pourquoi, valeurs} — the first true situation of PHRASES.md § 2."""
    ident, values = _pick(s)
    out = phrases.banner(ident, values)
    out["valeurs"] = values
    return out


def _pick(s: Situation) -> tuple[str, dict]:
    tz = s.tz
    machines = s.machines
    bought = s.bought_w
    sent = s.sent_w or 0.0
    hc_at = s.next_change[0] if s.next_change and s.next_change[1] == "hc" else None

    # 1. Urgent (red).
    if s.water_leak_min is not None and s.water_leak_min >= 40 and s.water_litres_per_day is not None:
        hours, minutes = divmod(int(s.water_leak_min), 60)
        return "fuite_eau", {"duree": f"{hours} h {minutes:02d}" if hours else f"{minutes} min",
                             "litres_par_jour": round(s.water_litres_per_day)}
    if bought is not None and s.subscribed_w and bought >= BREAKER_SHARE * s.subscribed_w:
        big = sorted(s.running, key=lambda r: -r.watts)[:3]
        if big:
            return "disjoncteur", {"appareils_en_marche": _names(big)}

    # 2. A gesture for next time (orange).
    if s.sunny and len(machines) >= 2 and s.sun_w >= 0.6 * machines[0].watts and (bought or 0) >= COVERED_W:
        return "machines_ensemble", {}
    if machines and (bought or 0) >= COVERED_W and s.period != "hc":
        if s.sunny and s.sun_peak is not None:
            return "machine_sans_soleil", {"machine": _the(machines[0]), "heure_pic": _quarter(s.sun_peak, tz)}
        # PHRASES.md: « une machine tourne la nuit en heures pleines ». By day with some sun and no forecast, no
        # sentence of PHRASES.md says when it would have been better: nothing orange is said (never an invented hour).
        if s.period == "hp" and hc_at is not None and not s.sunny:
            return "machine_heures_pleines", {"machine": _the(machines[0]), "heure_hc": _minute(hc_at, tz)}
    heater = next((r for r in s.running if r.kind == "chauffe_eau" and r.watts >= MACHINE_W), None)
    if heater and s.period == "hp" and (bought or 0) >= 0.5 * heater.watts and (hc_at is not None or s.sun_peak is not None):
        return "chauffe_eau_reseau", {}
    for r in s.running:
        normal = s.watched.get(r.name)
        if normal and r.hours_on is not None and r.hours_on > normal:
            return "oublie", {"appareil": r.name, "duree": f"{int(r.hours_on)} h"}

    # 3. A benefit to take (green), only while the sun kept is worth less than the off-peak hours (guard of card 3).
    worth = s.export_price is None or s.offpeak_price is None or s.export_price < s.offpeak_price
    if s.sunny and sent >= SURPLUS_W and worth:
        if machines:
            return "soleil_machine_ok", {"machine": _the(machines[0])}
        return "soleil_en_trop", {"surplus": f"{sent / 1000:.1f}".replace(".", ",")}
    if s.sunny and machines and bought is not None and bought < 100:
        return "soleil_machine_ok", {"machine": _the(machines[0])}

    # 4. Nothing to do (blue), with the next useful thing.
    if s.sunny and sent >= SMALL_SURPLUS_W:
        return "rien_soleil_petit", {}
    if s.sunny and bought is not None and bought < COVERED_W:
        return "rien_soleil_juste", {}
    if s.period == "hc" and s.offpeak_end is not None:
        return "rien_hc", {"heure_fin": _minute(s.offpeak_end, tz)}
    if not s.sunny and s.sun_peak is not None:
        return "rien_soleil_plus_tard", {"heure_pic": _quarter(s.sun_peak, tz)}
    if s.period == "hp" and hc_at is not None and (hc_at - s.now).total_seconds() <= HC_SOON_H * 3600:
        return "rien_hc_bientot", {"heure_hc": _minute(hc_at, tz)}
    return "rien", {}


class Steady:
    """The banner as shown: a new situation replaces the one shown only once it has held for `hold` (red at once).

    PHRASES.md § 8: a banner that changes more than 6 times a day is too nervous. A cloud that passes, a kettle, the
    dishwasher's pump between two heatings: none of them should make the banner blink.
    """

    def __init__(self, hold_minutes: float = 20):
        self.hold = hold_minutes * 60
        self.shown: dict | None = None
        self._candidate: dict | None = None
        self._since: datetime | None = None

    def update(self, banner: dict, now: datetime) -> dict:
        if self.shown is None or banner["couleur"] == phrases.URGENT or banner["id"] == self.shown["id"]:
            self.shown, self._candidate, self._since = banner, None, None
            return self.shown
        if self._candidate is None or self._candidate["id"] != banner["id"]:
            self._candidate, self._since = banner, now
        if (now - self._since).total_seconds() >= self.hold:
            self.shown, self._candidate, self._since = banner, None, None
        return self.shown
