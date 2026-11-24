"""A Linky with a register per period and per season, and one for the peak days (issue 18, an Enercoop « 2 saisons »
offer). An invented home: five registers, each with its own price on the Energy page."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from zoneinfo import ZoneInfo

from replay import ROOT  # noqa: F401 - puts the engine on the path
from engine import stats, tariff
from engine.home import Reading
from engine.sources import EnergyPage, Meter, Price, _period

PARIS = ZoneInfo("Europe/Paris")
NOW = datetime(2026, 11, 20, 15, 30, tzinfo=timezone.utc)
# (statistic, name on the Energy page, price)
REGISTERS = [
    ("sensor.linky_easf01", "HP hiver", 0.21114),
    ("sensor.linky_easf02", "HC hiver", 0.14949),
    ("sensor.linky_easf03", "HP été", 0.13251),
    ("sensor.linky_easf04", "HC été", 0.08408),
    ("sensor.linky_easf05", "Pointe", 0.41725),
]


def series(stat: str, kwh: float, days: int = 20) -> stats.Series:
    """`kwh` each hour over the last `days` days."""
    start = NOW.replace(minute=0) - timedelta(days=days)
    return stats.Series(stat, [stats.Hour(start + timedelta(hours=h), kwh) for h in range(days * 24)])


def page() -> EnergyPage:
    return EnergyPage("2026", imports=[Meter("import", s, n, Price(number=p), period=_period(n, s)) for s, n, p in REGISTERS])


class Names(unittest.TestCase):
    def test_each_register_says_its_period(self):
        self.assertEqual([m.period for m in page().imports], ["hp", "hc", "hp", "hc", "hp"])

    def test_the_period_of_the_linky(self):
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            from custom_components.hestia_energy import reader
        except ImportError:
            self.skipTest("Home Assistant is not installed")
        self.assertEqual(reader.period_of("H CREUSE HIVER"), "hc")
        self.assertEqual(reader.period_of("H PLEINE ETE"), "hp")
        self.assertEqual(reader.period_of("H POINTE"), "hp")
        for label in ("H CREUSE HIVER", "H POINTE", "HEURES CREUSES", "HC.."):
            self.assertTrue(reader._PERIOD_STATE.match(label), label)
        self.assertIsNone(reader._PERIOD_STATE.match("Hors gel"))


class Cost(unittest.TestCase):
    def test_each_register_is_counted_at_its_own_price(self):
        winter_hc, summer_hc = series("sensor.linky_easf02", 1.0), series("sensor.linky_easf04", 0.0)
        contract = tariff.Contract(tariff.HPHC, 9, None, {"hc": 0.08408})
        end = NOW.replace(minute=0)
        start = end - timedelta(days=1)
        # Before: the winter off-peak kWh at the summer off-peak price, the last meter read.
        before = tariff.cost(contract, {}, PARIS, [(winter_hc, "hc"), (summer_hc, "hc")], start, end)
        self.assertAlmostEqual(before.eur, 24 * 0.08408, places=3)
        contract.meter_prices = {"sensor.linky_easf02": 0.14949, "sensor.linky_easf04": 0.08408}
        after = tariff.cost(contract, {}, PARIS, [(winter_hc, "hc"), (summer_hc, "hc")], start, end)
        self.assertAlmostEqual(after.eur, 24 * 0.14949, places=3)
        self.assertTrue(after.complete)


class Coordinator(unittest.TestCase):
    def setUp(self):
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            from custom_components.hestia_energy import coordinator
        except ImportError:
            self.skipTest("Home Assistant is not installed")
        self.module = coordinator
        # Winter: the winter registers count, the summer ones are still, the peak one counted one day.
        counts = {"sensor.linky_easf01": 1.0, "sensor.linky_easf02": 0.6, "sensor.linky_easf03": 0.0,
                  "sensor.linky_easf04": 0.0, "sensor.linky_easf05": 0.0}
        p = page()
        readings = {m.stat: Reading(m, series(m.stat, counts[m.stat])) for m in p.imports}
        readings["sensor.linky_easf05"] = Reading(p.imports[4], series("sensor.linky_easf05", 1.5, days=1))
        changed = {"sensor.linky_easf01": NOW - timedelta(days=1), "sensor.linky_easf02": NOW - timedelta(minutes=2)}
        states = {s: SimpleNamespace(state="0", last_changed=changed.get(s, NOW - timedelta(days=200))) for s, _, _ in REGISTERS}
        c = coordinator.EnergyCoordinator.__new__(coordinator.EnergyCoordinator)
        c.hass = SimpleNamespace(states=SimpleNamespace(get=states.get))
        c.page = p
        c.home = SimpleNamespace(of=lambda kind: list(readings.values()) if kind == "import" else [])
        c.extras = {"period": None}
        c.offpeak = None
        self.c = c

    def test_the_prices_of_this_season(self):
        prices = self.c._prices(NOW)
        self.assertEqual(prices, {"hp": 0.21114, "hc": 0.14949})
        self.assertEqual(len(self.c.meter_prices), 5)

    def test_the_register_counting_now_gives_the_period(self):
        self.c._prices(NOW)
        self.c.contract = tariff.Contract(tariff.HPHC, 9, None, {}, meter_prices=dict(self.c.meter_prices))
        self.assertEqual(self.c._active_register(NOW).stat, "sensor.linky_easf02")
        self.assertEqual(self.c._period(NOW), "hc")

    def test_two_meters_one_per_period_change_nothing(self):
        self.c.page = EnergyPage("2026", imports=self.c.page.imports[:2])
        self.assertEqual(self.c._prices(NOW), {"hp": 0.21114, "hc": 0.14949})
        self.assertEqual(self.c.meter_prices, {})


if __name__ == "__main__":
    unittest.main()
