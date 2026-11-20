"""The reviews of yesterday, last week and last month (2.9), replayed on Frank's real year."""
from datetime import datetime
import unittest
from zoneinfo import ZoneInfo

from replay import need
from engine import report, tariff
from test_home import franks_home

PARIS = ZoneInfo("Europe/Paris")


class Reviews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        need()
        home = franks_home()
        hp = next(r.series for r in home.of("import") if r.meter.period == "hp")
        hc = next(r.series for r in home.of("import") if r.meter.period == "hc")
        cls.home, cls.table = home, tariff.load_regulated()
        cls.contract = report.contract_for(home, 9, tariff.learn_offpeak(hp, hc, PARIS), {}, None, None)

    def test_the_5th_of_november(self):
        found = {r["id"]: r for r in report.reviews(self.home, self.contract, self.table, datetime(2026, 11, 5, 10, tzinfo=PARIS))}
        self.assertTrue(found["hier"]["titre"].startswith("Hier : "))
        self.assertEqual(found["hier"]["texte"], "18 kWh · le soleil a couvert 17 % · 1,32 € de plus que le mercredi d'avant.")
        self.assertEqual(found["semaine"]["titre"], "La semaine dernière : 24 €")
        # October 2025 is before the replay's year: no comparison, never an invented one.
        self.assertEqual(found["mois"]["titre"], "Octobre : 88 €")       # with the « majoration auto-producteur »
        self.assertNotIn("que", found["mois"]["texte"])

    def test_a_small_gap_is_not_worth_a_word(self):
        found = {r["id"]: r for r in report.reviews(self.home, self.contract, self.table, datetime(2026, 9, 2, 10, tzinfo=PARIS))}
        self.assertEqual(found["hier"]["texte"], "12 kWh · le soleil a couvert 45 %.")


if __name__ == "__main__":
    unittest.main()


class SoFar(unittest.TestCase):
    def test_today_against_yesterday_at_the_same_hour(self):
        Reviews.setUpClass()
        found = report.so_far(Reviews.home, Reviews.contract, Reviews.table, datetime(2026, 11, 5, 18, 40, tzinfo=PARIS))
        self.assertEqual(found["jusqu_a"], "2026-11-05T18:00:00+01:00")
        self.assertIsNotNone(found["euros"])
        self.assertIsNotNone(found["hier_euros"])
        self.assertIsNone(report.so_far(Reviews.home, Reviews.contract, Reviews.table, datetime(2026, 11, 5, 0, 30, tzinfo=PARIS)))


class SunShort(unittest.TestCase):
    """Prod, 19 Nov. 2026: 9.4 kWh bought, 4.4 kWh of sun and 5.5 kWh sent. More sent than produced is impossible:
    the card said « le soleil a couvert 0 % ». The shares are now unknown (no real data needed)."""

    def period(self, bought, sun, sent):
        day = datetime(2026, 11, 19, tzinfo=PARIS)
        return report.Period(day, day, bought, 2.0, 0.6, 0, sun, sent)

    def test_more_sent_than_produced_is_not_known(self):
        p = self.period(9.37, 4.38, 5.51)
        self.assertIsNone(p.sun_cover)
        self.assertIsNone(p.sun_kept)
        self.assertIsNone(p.as_dict()["soleil_couvre"])

    def test_an_ordinary_day_keeps_its_shares(self):
        p = self.period(12.36, 4.94, 1.69)
        self.assertEqual(round(p.sun_cover * 100), 21)
        self.assertEqual(round(p.sun_kept * 100), 66)
