"""Heating estimated from the cold (lot 9.2, palier 0): no heating meter needed.

Each day, the home's consumption is set against how cold it was (the degree-days Hestia Weather gives, base 18 °C).
What rises with the cold is the heating; what stays in summer is the rest. Said to the user in one sentence and one
figure (« Chauffage ≈ 95 € ce mois, estimé »), never with the method's words.

Pure Python: the days and degree-days come in, the estimate goes out.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

# Below this share of the day-to-day differences explained by the cold, the link is too loose to give a figure: the
# home is heated mostly by another energy (stove, gas…), and the brick says so instead of inventing one.
MIN_FIT = 0.5
MIN_DAYS = 60          # days with both a complete consumption and a temperature
MIN_COLD_DAYS = 20     # of which days that needed heating (more than 2 degree-days)


@dataclass(frozen=True)
class Learned:
    rest_kwh: float        # what the home uses per day without heating (the summer)
    per_degree_kwh: float  # what each degree-day of cold adds
    fit: float             # share of the differences the cold explains, 0 to 1
    days: int

    @property
    def reliable(self) -> bool:
        return self.fit >= MIN_FIT and self.per_degree_kwh > 0

    def heat_kwh(self, degree_days: float | None) -> float | None:
        """A day's heating, estimated: what the cold of that day adds. None when its cold is unknown."""
        if degree_days is None or not self.reliable:
            return None
        return self.per_degree_kwh * max(0.0, degree_days)


def learn(used: dict[date, float], degree_days: dict[date, float]) -> Learned | None:
    """The line through each day's (cold, consumption). None with too few days to say anything."""
    points = [(degree_days[d], kwh) for d, kwh in used.items() if degree_days.get(d) is not None]
    if len(points) < MIN_DAYS or sum(1 for x, _ in points if x > 2) < MIN_COLD_DAYS:
        return None
    n = len(points)
    mx = sum(x for x, _ in points) / n
    my = sum(y for _, y in points) / n
    sxx = sum((x - mx) ** 2 for x, _ in points)
    syy = sum((y - my) ** 2 for _, y in points)
    if sxx == 0 or syy == 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in points)
    slope = sxy / sxx
    return Learned(rest_kwh=my - slope * mx, per_degree_kwh=slope, fit=sxy * sxy / (sxx * syy), days=n)


@dataclass(frozen=True)
class Heat:
    kwh: float
    eur: float | None
    days: int          # days counted (those whose cold is known)

    def as_dict(self) -> dict:
        return {"kwh": round(self.kwh, 1), "eur": None if self.eur is None else round(self.eur, 2), "jours": self.days}


def over(learned: Learned | None, degree_days: dict[date, float], first: date, last: date,
         bought_kwh: float | None = None, energy_eur: float | None = None) -> Heat | None:
    """The heating of the days from `first` to `last` (included), in kWh, and in euros at the period's own average
    price of the electricity bought (heating is bought electricity, mostly in winter). None when not reliable."""
    if learned is None or not learned.reliable:
        return None
    total, counted, day = 0.0, 0, first
    while day <= last:
        kwh = learned.heat_kwh(degree_days.get(day))
        if kwh is not None:
            total += kwh
            counted += 1
        day += timedelta(days=1)
    if not counted:
        return None
    eur = None
    if bought_kwh and energy_eur is not None and bought_kwh > 0:
        eur = total * energy_eur / bought_kwh
    return Heat(total, eur, counted)


# --- The pellet stove (9.1), read from Suivi Stock Pellet ---------------------------------------------------------

PELLET_KWH_PER_KG = 4.6   # the usual heat of a kilo of pellets; Suivi Stock Pellet gives its own when set


def price_per_kg(spent_eur: float | None, bought_kg: float | None, bag_price: float | None,
                 bag_kg: float | None) -> float | None:
    """What a kilo of pellets costs: what the season's purchases cost (Suivi Stock Pellet), else the bag's price the
    household gave. None when neither is known: kilos are then shown without euros, never as free."""
    if spent_eur and bought_kg and bought_kg > 0:
        return spent_eur / bought_kg
    if bag_price and bag_kg and bag_kg > 0:
        return bag_price / bag_kg
    return None


@dataclass(frozen=True)
class Pellets:
    kg: float
    eur: float | None

    def as_dict(self) -> dict:
        return {"kg": round(self.kg, 1), "eur": None if self.eur is None else round(self.eur, 2)}


def pellets(kg: float | None, per_kg: float | None) -> Pellets | None:
    if kg is None:
        return None
    return Pellets(max(0.0, kg), None if per_kg is None else max(0.0, kg) * per_kg)


# --- Heating now (9.5, palier 1): the thermostats that heat, and what they draw ------------------------------------

@dataclass(frozen=True)
class Thermostat:
    name: str
    heating: bool
    watts: float | None    # what it draws when it heats (Versatile Thermostat's own figure), None when unknown
    stove: bool            # it lights a stove (pellets, wood): heat, but no electricity to count


@dataclass(frozen=True)
class HeatingNow:
    rooms: tuple[tuple[str, float | None], ...]  # the electric heaters heating now, each with what it draws
    watts: float | None       # what those with a known power draw together (None: none known)
    unknown: tuple[str, ...]  # heating, but their power is not known: named, never guessed
    stove: bool               # the stove is heating

    def as_dict(self, price: float | None) -> dict:
        eur = None if self.watts is None or price is None else round(self.watts / 1000 * price, 2)
        return {"pieces": [{"nom": n, "w": None if w is None else round(w)} for n, w in self.rooms], "w": None if self.watts is None else round(self.watts),
                "euros_de_l_heure": eur, "sans_puissance": list(self.unknown), "poele": self.stove}


def now(thermostats: list[Thermostat]) -> HeatingNow | None:
    """None when no thermostat is known (nothing to say); else who heats and what it draws."""
    if not thermostats:
        return None
    electric = [t for t in thermostats if t.heating and not t.stove]
    known = [t.watts for t in electric if t.watts is not None]
    return HeatingNow(tuple((t.name, t.watts) for t in electric), sum(known) if known else None,
                      tuple(t.name for t in electric if t.watts is None), any(t.heating and t.stove for t in thermostats))
