"""The unusual day (5.1) replayed on Frank's real year: about one day a month above the usual, a few absences below."""
from datetime import date
import unittest

from replay import degree_days, need
from engine import anomaly, heating, phrases
from test_home import franks_home


class UnusualDays(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        need()
        cls.used = franks_home().used_days()
        cls.cold = degree_days()
        cls.learned = heating.learn(cls.used, cls.cold)

    def flagged(self, learned, cold):
        found = {d: anomaly.check(d, self.used, learned, cold) for d in self.used}
        return {d: u for d, u in found.items() if u is not None}

    def test_with_the_cold(self):
        found = self.flagged(self.learned, self.cold)
        more = sorted(d for d, u in found.items() if u.more)
        less = sorted(d for d, u in found.items() if not u.more)
        self.assertEqual(len(more), 11)
        self.assertEqual(len(less), 6)
        self.assertIn(date(2025, 12, 24), more)       # Christmas Eve: 54 kWh for 31 usual
        self.assertIn(date(2026, 7, 14), less)        # away in July
        self.assertTrue(found[date(2025, 12, 24)].with_cold)

    def test_without_hestia_weather_the_same_weekdays(self):
        found = self.flagged(None, {})
        self.assertTrue(found)
        self.assertTrue(all(not u.with_cold for u in found.values()))
        self.assertLess(len(found), 60)               # never a day in six

    def test_the_sentence(self):
        u = anomaly.check(date(2025, 12, 24), self.used, self.learned, self.cold)
        text = phrases.know("jour_plus_froid", {"kwh": phrases.number(u.used_kwh), "ecart": phrases.number(u.gap_kwh),
                                                "euros": phrases.euros(u.gap_kwh * 0.2)})
        self.assertEqual(text, "Hier, la maison a consommé 54 kWh : 22 de plus que d'habitude pour ce froid, environ 4,42 €.")


if __name__ == "__main__":
    unittest.main()


class ForgottenDevices(unittest.TestCase):
    """5.2 on Frank's real devices: each one's usual runs, learned from its own hours."""

    @classmethod
    def setUpClass(cls):
        from replay import description, hourly
        from engine.sources import read_page
        need()
        rows = hourly()
        cls.rate = {m.name: rows.get(m.power.rate) or [] for m in read_page(description()["page_energie"]).devices}

    def test_learned_limits(self):
        self.assertEqual(anomaly.run_limit(self.rate["Lave vaisselle"]), 8)     # runs up to 4 h: asked after 8 h
        self.assertEqual(anomaly.run_limit(self.rate["Four"]), 6)
        self.assertEqual(anomaly.run_limit(self.rate["Frigo"]), 5)
        self.assertIsNone(anomaly.run_limit(self.rate["Domotique"]))            # always on: never « forgotten »

    def test_the_hours_on_in_a_row(self):
        rows = [{"mean": 0}, {"mean": 900}, {"mean": 1200}, {"mean": 800}]
        self.assertEqual(anomaly.trailing_hours(rows), 3)
        self.assertEqual(anomaly.trailing_hours(rows + [{"mean": 10}]), 0)
