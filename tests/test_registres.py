"""A Linky with a register per period and per season, and one for the peak days (issue 18, an Enercoop « 2 saisons »
offer). An invented home: five registers, each with its own price on the Energy page."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
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


def two_seasons_meters(days: int = 28, end: datetime | None = None) -> tuple[stats.Series, stats.Series]:
    """A winter week of the offer: off-peak 0 h - 7 h and 13 h - 16 h on working days, all day on rest days."""
    end = end or datetime(2026, 11, 21, 23, tzinfo=PARIS).astimezone(timezone.utc)
    hp, hc = stats.Series("sensor.hp"), stats.Series("sensor.hc")
    for n in range(days * 24, 0, -1):
        start = end - timedelta(hours=n)
        local = start.astimezone(PARIS)
        off = tariff.rest_day(local.date()) or local.hour < 7 or 13 <= local.hour < 16
        hp.hours.append(stats.Hour(start, 0.0 if off else 0.5))
        hc.hours.append(stats.Hour(start, 0.5 if off else 0.0))
    return hp, hc


class Weekends(unittest.TestCase):
    def test_the_french_public_holidays(self):
        days = tariff.holidays(2026)
        self.assertEqual(len(days), 11)
        for day in (date(2026, 4, 6), date(2026, 5, 14), date(2026, 5, 25), date(2026, 7, 14), date(2026, 11, 11)):
            self.assertIn(day, days)
        self.assertIn(date(2027, 3, 29), tariff.holidays(2027))  # Easter Monday 2027
        self.assertTrue(tariff.rest_day(date(2026, 11, 21)))      # a Saturday
        self.assertFalse(tariff.rest_day(date(2026, 11, 20)))     # a Friday

    def test_a_weekend_off_peak_all_day_is_learned_apart(self):
        learned = tariff.learn_offpeak(*two_seasons_meters(), PARIS)
        self.assertTrue(learned.weekend_all)
        self.assertEqual([r.label() for r in learned.ranges], [("0 h", "7 h"), ("13 h", "16 h")])
        saturday = datetime(2026, 11, 21, 18, tzinfo=PARIS)
        self.assertTrue(learned.contains(saturday, PARIS))
        self.assertFalse(learned.contains(datetime(2026, 11, 20, 18, tzinfo=PARIS), PARIS))
        self.assertTrue(learned.contains(datetime(2026, 11, 11, 18, tzinfo=PARIS), PARIS))  # 11 November
        # Saturday evening: the off-peak hours go on until Monday 7 h.
        at, period = tariff.next_change(learned, saturday, PARIS)
        self.assertEqual((at.astimezone(PARIS), period), (datetime(2026, 11, 23, 7, tzinfo=PARIS), "hp"))

    def test_the_same_hours_every_day_stay_as_before(self):
        hp, hc = stats.Series("sensor.hp"), stats.Series("sensor.hc")
        end = datetime(2026, 11, 21, 23, tzinfo=PARIS).astimezone(timezone.utc)
        for n in range(28 * 24, 0, -1):
            start = end - timedelta(hours=n)
            off = start.astimezone(PARIS).hour < 6 or start.astimezone(PARIS).hour >= 22
            hp.hours.append(stats.Hour(start, 0.0 if off else 0.5))
            hc.hours.append(stats.Hour(start, 0.5 if off else 0.0))
        learned = tariff.learn_offpeak(hp, hc, PARIS)
        self.assertFalse(learned.weekend_all)
        self.assertEqual([r.label() for r in learned.ranges], [("22 h", "6 h")])
        self.assertFalse(learned.contains(datetime(2026, 11, 21, 18, tzinfo=PARIS), PARIS))

    def test_the_household_says_for_the_weekend(self):
        typed = tariff.parse_offpeak("00:00-07:00, 13:00-16:00")
        self.assertFalse(typed.weekend_all)
        found = tariff.learn_offpeak(*two_seasons_meters(), PARIS)
        self.assertTrue(tariff.with_weekend(typed, None, found).weekend_all)   # what the meters show
        self.assertTrue(tariff.with_weekend(typed, "tout").weekend_all)
        self.assertFalse(tariff.with_weekend(typed, "pareil", found).weekend_all)
        self.assertIsNone(tariff.with_weekend(None, "tout"))

    def test_the_sentence(self):
        from engine import phrases
        text = phrases.know("hc_plages", {"h1": "0 h", "h2": "7 h", "h3": "13 h", "h4": "16 h",
                                          "avec": (" en semaine, toute la journée le week-end et les jours fériés",)})
        self.assertEqual(text, "Heures creuses de 0 h à 7 h et de 13 h à 16 h en semaine, toute la journée le week-end et les jours fériés.")


class Service(unittest.TestCase):
    def test_an_automation_sets_the_contract(self):
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            from custom_components.hestia_energy import websocket
            import voluptuous as vol
        except ImportError:
            self.skipTest("Home Assistant is not installed")
        data = websocket.SERVICE_SCHEMA({"offpeak": "00:00-07:00, 13:00-16:00", "offpeak_weekend": "tout",
                                         "offer": "autre", "price_hp": 0.21114, "price_hc": 0.14949, "kva": "9"})
        self.assertEqual(data["kva"], 9)
        for wrong in ({"offpeak": "toute la nuit"}, {"offpeak_weekend": "parfois"}, {"groups": {}}, {"price_hp": 9}):
            with self.assertRaises(vol.Invalid):
                websocket.SERVICE_SCHEMA(wrong)


if __name__ == "__main__":
    unittest.main()
