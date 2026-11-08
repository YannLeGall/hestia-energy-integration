"""The night baseload and the banner, replayed on Frank's real year (lots 2.4, 4.1, 4.2, 4.7; PHRASES.md § 8)."""
import collections
import csv
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
import unittest
from zoneinfo import ZoneInfo

from replay import LEVEL0, description, hourly, need, situations
from engine import advice, baseline, home as H, phrases, stats, tariff
from engine.sources import read_page

PARIS = ZoneInfo("Europe/Paris")


@lru_cache(maxsize=1)
def franks_home():
    rows = hourly()
    channels = sorted(k for k in rows if k.endswith(("_ch1_power", "_ch2_power")))
    return H.build(read_page(description()["page_energie"]), rows, PARIS, datetime(2025, 11, 7, 8, tzinfo=timezone.utc), 9, channels)


@lru_cache(maxsize=4)
def replay(end: date, days: int = 30):
    home = franks_home()
    peak, offpeak = [r.series for r in home.of("import")]
    learned = tariff.learn_offpeak(peak, offpeak, PARIS)
    stop = datetime.combine(end, datetime.min.time(), PARIS)
    steady = advice.Steady()
    return [(s.now, advice.choose(s), steady.update(advice.choose(s), s.now))
            for s in situations(home, hourly(), learned, stop - timedelta(days=days), stop, 9, 0.1276, 0.1589)]


class Baseload(unittest.TestCase):
    def test_the_baseload_holds_all_year_heating_or_not(self):
        bought = franks_home().bought
        for day in (date(2026, 1, 15), date(2026, 6, 15), date(2026, 11, 6)):
            self.assertTrue(180 <= baseline.baseload(bought, PARIS, day).watts <= 290, day)
            self.assertIsNone(baseline.rise(bought, PARIS, day))

    def test_a_plain_linky_gives_the_same_baseload(self):
        need(LEVEL0)
        with open(LEVEL0 / "achats-reseau-par-heure-21-jours.csv", newline="") as f:
            linky = stats.Series("linky", [stats.Hour(datetime.fromisoformat(r["debut_utc"]), float(r["kwh_achetes"]))
                                           for r in csv.DictReader(f)])
        self.assertEqual(baseline.baseload(linky, PARIS).watts, baseline.baseload(franks_home().bought, PARIS).watts)

    def test_its_euros_a_year(self):
        euros = baseline.yearly_euros(190, baseline.average_price(0.2142, 0.1589))
        self.assertAlmostEqual(euros, 326, delta=1)


class Banner(unittest.TestCase):
    def test_never_more_than_seven_changes_a_day(self):
        for end in (date(2026, 11, 7), date(2026, 6, 30), date(2026, 1, 31)):
            changes = collections.Counter()
            previous = None
            for moment, _, shown in replay(end):
                if previous and shown["id"] != previous["id"]:
                    changes[moment.astimezone(PARIS).date()] += 1
                previous = shown
            self.assertLessEqual(max(changes.values()), 7, end)
            self.assertLessEqual(sum(changes.values()) / 30, 5.5, end)

    def test_the_water_heater_on_the_grid_in_winter(self):
        # A5, 1: the water heater runs 11 h to 14 h 30 whatever the sun; in January it heats on the grid in peak hours.
        ids = collections.Counter(chosen["id"] for _, chosen, _ in replay(date(2026, 1, 31)))
        self.assertGreater(ids["chauffe_eau_reseau"], 20)

    def test_the_sun_in_june(self):
        ids = collections.Counter(chosen["id"] for _, chosen, _ in replay(date(2026, 6, 30)))
        self.assertGreater(ids["soleil_en_trop"], 150)

    def test_every_banner_is_a_sentence_of_phrases_md(self):
        for _, chosen, _ in replay(date(2026, 11, 7)):
            self.assertIn(chosen["id"], phrases.BANNER)
            self.assertNotIn("{", chosen["titre"] + chosen["pourquoi"])

    def test_the_29th_of_october(self):
        day = {m.astimezone(PARIS).hour: chosen for m, chosen, _ in replay(date(2026, 11, 7)) if m.astimezone(PARIS).date() == date(2026, 10, 29)}
        self.assertEqual(day[3]["titre"] + " " + day[3]["pourquoi"],
                         "Rien à faire. Heures creuses jusqu'à 8 h 19 : c'est le bon moment pour les machines.")
        self.assertEqual(day[10]["id"], "soleil_en_trop")
        self.assertEqual(day[22]["id"], "rien_hc_bientot")


class Labo(unittest.TestCase):
    def test_a_dishwasher_by_day_in_some_sun_is_not_told_to_wait_for_the_night(self):
        # Seen at the labo on 7 Nov. 2026, 13 h 55: 1.9 kW of sun, 892 W bought, the dishwasher at 1 737 W, peak hours.
        # « Heures pleines pour le lave vaisselle » is the night's sentence (PHRASES.md); without a forecast, no
        # sentence says when the sun would have been enough: nothing orange.
        now = datetime(2026, 11, 7, 12, 55, tzinfo=timezone.utc)
        s = advice.Situation(now=now, tz=PARIS, period="hp", next_change=(datetime(2026, 11, 8, 0, 14, tzinfo=PARIS), "hc"),
                             bought_w=892, sent_w=0, sun_w=1921, subscribed_w=9000,
                             running=[advice.Running("Lave vaisselle", "machine", 1737), advice.Running("Sèche linge", "machine", 541)])
        self.assertNotEqual(advice.choose(s)["couleur"], "orange")
        s.sun_w = 0
        self.assertEqual(advice.choose(s)["id"], "machine_heures_pleines")


class Words(unittest.TestCase):
    def test_kinds_of_devices(self):
        self.assertEqual([advice.kind_of(n) for n in ("Lave linge", "Sèche linge", "Chauffe eau", "Four", "Chauffage Salon 1", "Sèche serviettes P", "Frigo")],
                         ["machine", "machine", "chauffe_eau", "cuisson", "chauffage", "seche_serviettes", "froid"])

    def test_an_optional_part_is_left_out(self):
        self.assertEqual(phrases.fill("[Ce soir,] allumez-le plutôt.", {}), "Allumez-le plutôt.")
        self.assertEqual(phrases.fill("[Ce soir,] allumez-le plutôt.", {"avec": ["Ce soir,"]}), "Ce soir, allumez-le plutôt.")


if __name__ == "__main__":
    unittest.main()
