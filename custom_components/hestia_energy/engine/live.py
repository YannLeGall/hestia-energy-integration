"""The arbiter of the live measures (lot 1.2, D7, F1.7): for each quantity, the source to believe now, and why.

Each candidate is judged on what it does, not on its « local » or « cloud » label:
1. unavailable or not a number: set aside;
2. frozen: unchanged for 30 minutes while another source of the same quantity moved and disagrees (Frank's
   « Total puissance produite instantanée » at 0 W since 23 h 34 while OpenDTU gives 2 083 W);
3. silent (not reported for 15 minutes, nobody contradicting it): set aside for the live view (« en attente »);
4. late: its statistics come an hour after its power (health.lag): kept, behind the others;
then the freshest wins; within a minute of each other, the local one first (it survives an internet cut-off).

Plain Python: states come in as small `Reading`s built from Home Assistant's states.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

SILENT_S = 15 * 60
FROZEN_S = 30 * 60
TIE_S = 60
DISAGREE_W = 200
DISAGREE_SHARE = 0.3

# Units brought to W. VA is taken as W: a home's power factor is close to 1 and it only ever serves as an order of size.
_TO_W = {"W": 1.0, "kW": 1000.0, "MW": 1e6, "VA": 1.0, "kVA": 1000.0}


@dataclass(frozen=True)
class Reading:
    entity_id: str
    state: str
    unit: str | None
    changed: datetime
    reported: datetime

    @property
    def watts(self) -> float | None:
        try:
            value = float(self.state)
        except (TypeError, ValueError):
            return None
        factor = _TO_W.get(self.unit or "W")
        return None if factor is None else value * factor


@dataclass
class Candidate:
    """One way to know a quantity: one entity or a sum of entities (each with its sign)."""
    name: str
    parts: list[tuple[Reading, float]]
    local: bool | None = None
    late: bool = False

    def value(self) -> float | None:
        values = [r.watts for r, _ in self.parts]
        if any(v is None for v in values):
            return None
        return sum(v * sign for v, (_, sign) in zip(values, self.parts))

    def changed(self) -> datetime:
        return max(r.changed for r, _ in self.parts)

    def reported(self) -> datetime:
        """When the source last spoke: its stalest part, leaving out the parts at 0 W. A meter at rest that stops
        reporting has nothing to say (the off-peak meter during peak hours, the panels at night): it must not silence
        the part that measures (labo, 19 Nov. 2026: « Page Énergie » set aside 15 min after a restart, its peak-hours
        meter alive every 15 s). All parts at rest: the freshest of them."""
        busy = [r.reported for r, _ in self.parts if r.watts != 0]
        return min(busy) if busy else max(r.reported for r, _ in self.parts)


@dataclass
class Verdict:
    quantity: str
    chosen: Candidate | None
    value: float | None
    set_aside: list[tuple[Candidate, str, dict]] = field(default_factory=list)


def judge(quantity: str, candidates: list[Candidate], now: datetime) -> Verdict:
    """The source to believe for one quantity, and every other one with the reason it was set aside."""
    verdict = Verdict(quantity, None, None)
    alive, silent = [], []
    for c in candidates:
        if not c.parts or c.value() is None:
            verdict.set_aside.append((c, "indisponible", {}))
        elif (now - c.reported()).total_seconds() > SILENT_S:
            silent.append(c)
        else:
            alive.append(c)
    moving = [c for c in alive if (now - c.changed()).total_seconds() < FROZEN_S]

    def contradicted(c: Candidate) -> Candidate | None:
        value = c.value()
        return next((o for o in moving if abs(o.value() - value) > max(DISAGREE_W, DISAGREE_SHARE * max(abs(o.value()), abs(value)))), None)

    kept = []
    for c in alive + silent:
        if c in moving:
            kept.append(c)
            continue
        proof = contradicted(c)
        if proof is not None:
            # A template that stopped (no report since) and a sensor stuck at one value are the same fault: frozen.
            verdict.set_aside.append((c, "fige", {"valeur": c.value(), "depuis": c.changed(), "preuve": proof.name, "preuve_valeur": proof.value()}))
        elif c in silent:
            verdict.set_aside.append((c, "muet", {"depuis": c.reported()}))
        else:
            kept.append(c)
    if not kept:
        return verdict

    def rank(c: Candidate):
        age = (now - c.reported()).total_seconds()
        return (c.late, age // TIE_S, c.local is not True)

    kept.sort(key=rank)
    verdict.chosen, verdict.value = kept[0], kept[0].value()
    for c in kept[1:]:
        verdict.set_aside.append((c, "controle", {"valeur": c.value()}))
    return verdict


@dataclass
class Flow:
    """Water flowing without a stop (lot 5.4): since when, and how much a day if it goes on."""
    since: datetime | None = None
    rate: float = 0.0          # litres per minute

    def update(self, litres_per_minute: float | None, now: datetime) -> None:
        if litres_per_minute is None:
            return
        if litres_per_minute > 0:
            if self.since is None:
                self.since = now
            self.rate = litres_per_minute
        else:
            self.since, self.rate = None, 0.0

    def minutes(self, now: datetime) -> float | None:
        return None if self.since is None else (now - self.since).total_seconds() / 60

    @property
    def litres_per_day(self) -> float:
        return self.rate * 1440
