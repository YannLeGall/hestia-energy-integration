"""Heating estimated from the cold (9.2), on Frank's real year: what rises with the cold, nothing invented."""
from datetime import date, timedelta
import unittest

from replay import degree_days, need
from engine import heating
from test_home import franks_home


class HeatingFromTheCold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        need()
        home = franks_home()
        cls.used = home.used_days()
        cls.cold = degree_days()
        cls.learned = heating.learn(cls.used, cls.cold)

    def test_franks_electricity_follows_the_cold(self):
        L = self.learned
        self.assertIsNotNone(L)
        self.assertTrue(L.reliable)
        self.assertAlmostEqual(L.per_degree_kwh, 1.67, delta=0.1)
        self.assertAlmostEqual(L.rest_kwh, 13, delta=1)

    def test_january_and_summer(self):
        jan = heating.over(self.learned, self.cold, date(2026, 1, 1), date(2026, 1, 31))
        self.assertAlmostEqual(jan.kwh, 600, delta=40)
        july = heating.over(self.learned, self.cold, date(2026, 7, 1), date(2026, 7, 31))
        self.assertEqual(round(july.kwh), 0)

    def test_euros_at_the_price_paid(self):
        heat = heating.over(self.learned, self.cold, date(2026, 1, 1), date(2026, 1, 31), bought_kwh=1000, energy_eur=250)
        self.assertAlmostEqual(heat.eur, heat.kwh * 0.25, places=6)

    def test_no_figure_when_the_cold_explains_little(self):
        """The same real days set against the cold of half a year later: no link, so no figure (a stove home)."""
        shifted = {d + timedelta(days=182): v for d, v in self.cold.items()}
        learned = heating.learn(self.used, shifted)
        self.assertTrue(learned is None or not learned.reliable)
        self.assertIsNone(heating.over(learned, shifted, date(2026, 1, 1), date(2026, 1, 31)))

    def test_too_few_days(self):
        few = dict(list(self.used.items())[:30])
        self.assertIsNone(heating.learn(few, self.cold))


if __name__ == "__main__":
    unittest.main()


class PelletStove(unittest.TestCase):
    """Frank's stove as Suivi Stock Pellet saw it on 7 Nov. 2026: 45 kg burnt this season, no purchase entered yet,
    bags of 15 kg at 5 €."""

    def test_the_bag_prices_the_kilo_when_no_purchase_is_entered(self):
        per_kg = heating.price_per_kg(spent_eur=0, bought_kg=0, bag_price=5.0, bag_kg=15.0)
        self.assertAlmostEqual(per_kg, 1 / 3)
        self.assertEqual(heating.pellets(45.0, per_kg).as_dict(), {"kg": 45.0, "eur": 15.0})

    def test_purchases_win_over_the_bag(self):
        self.assertAlmostEqual(heating.price_per_kg(spent_eur=390, bought_kg=1050, bag_price=5.0, bag_kg=15.0), 390 / 1050)

    def test_no_price_no_euros(self):
        self.assertEqual(heating.pellets(45.0, heating.price_per_kg(0, 0, None, 15.0)).as_dict(), {"kg": 45.0, "eur": None})


class HeatingNowTest(unittest.TestCase):
    """The thermostats copied at the lab on 7 Nov. 2026 at 20 h 32 (Versatile Thermostat's attributes)."""

    def setUp(self):
        T = heating.Thermostat
        self.seen = [T("Thermostat P", True, 1500.0, False), T("Thermostat M", False, 0.0, False),
                     T("Thermostat Poêle", True, 8500.0, True), T("Melissa", True, None, False)]

    def test_what_heats_and_what_it_draws(self):
        now = heating.now(self.seen)
        self.assertEqual(now.rooms, (("Thermostat P", 1500.0), ("Melissa", None)))
        self.assertEqual(now.watts, 1500.0)                 # the stove's 8.5 kW are pellets, not electricity
        self.assertEqual(now.unknown, ("Melissa",))
        self.assertTrue(now.stove)
        self.assertEqual(now.as_dict(0.2)["euros_de_l_heure"], 0.3)

    def test_no_thermostat_nothing_said(self):
        self.assertIsNone(heating.now([]))
