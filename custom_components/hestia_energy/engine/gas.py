"""The gas bill: what the gas burnt costs with its taxes, and what is paid whatever is burnt.

A French gas bill has four lines, then VAT on all of them: the subscription (a month), the gas burnt (kWh × the price
of a kWh), the CTA (« contribution tarifaire d'acheminement », a month) and the excise on the gas (« TICGN », euros a
MWh burnt). The Energy page only knows the price of one unit of the meter: the household gives the rest in Réglages,
as its bill shows it. Left empty, nothing is added and the page's price is taken as it is.

Pure Python.
"""
from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime

from .sources import GAS_VOLUME

# VAT on every line of a gas bill since 1 August 2025 (the subscription and the CTA paid 5.5 % before): the law's
# rate, not the home's, so not a setting.
VAT = 0.20
# What a cubic metre of gas gives in France, about: used until the household types its bill's own coefficient.
KWH_PER_M3 = 11.2
# No « à ce rythme » before three days of the month: one cold morning is not a month (report.projection's own rule).
MIN_DAYS = 3


@dataclass(frozen=True)
class Contract:
    """The gas contract as typed in Réglages; every line may be left empty."""
    price_kwh: float | None = None       # the bill's price of a kWh: replaces the Energy page's
    subscription: float | None = None    # euros a month
    cta: float | None = None             # euros a month
    excise: float | None = None          # the TICGN, euros a MWh
    before_tax: bool = False             # typed as the bill's lines before VAT: VAT is added to all, the price too
    kwh_per_m3: float | None = None      # the bill's conversion, for a meter that counts cubic metres

    def unit_price(self, unit: str | None, page: float | None) -> float | None:
        """What one unit of the meter (a kWh or a m³) costs, taxes included. None when no price is known: the gas is
        then shown without euros, never as free."""
        kwh = (self.kwh_per_m3 or KWH_PER_M3) if unit == GAS_VOLUME else 1.0     # the kWh in one unit of the meter
        price = page if self.price_kwh is None else self.price_kwh * kwh
        if price is None:
            return None
        price += (self.excise or 0.0) / 1000 * kwh
        return price * (1 + VAT) if self.before_tax else price

    def fixed_month(self) -> float | None:
        """The subscription and the CTA of one month, taxes included. None when neither was typed."""
        if self.subscription is None and self.cta is None:
            return None
        fixed = (self.subscription or 0.0) + (self.cta or 0.0)
        return fixed * (1 + VAT) if self.before_tax else fixed


def months(first: date, now: datetime) -> float:
    """The months from `first` (the first day of a month) to `now`, the month under way counted for its part."""
    whole = (now.year - first.year) * 12 + now.month - first.month
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return max(0.0, whole + (now - start).total_seconds() / 86400 / monthrange(now.year, now.month)[1])


def month_bill(burnt_eur: float | None, fixed: float | None, now: datetime) -> dict | None:
    """This month's bill: the gas burnt so far, what is paid whatever is burnt, and where the month ends at this pace
    (the gas stretched to the last day, the whole subscription). None without a subscription or without a price: the
    gas alone is already said."""
    if burnt_eur is None or fixed is None:
        return None
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elapsed = (now - start).total_seconds() / 86400
    end = None if elapsed < MIN_DAYS else burnt_eur * monthrange(now.year, now.month)[1] / elapsed + fixed
    return {"gaz": round(burnt_eur, 2), "fixe": round(fixed, 2), "fin_de_mois": None if end is None else round(end, 2)}
