"""A home with HA Linky only (palier 0, D21), on Frank's own HA Linky statistics: one meter, one value a day for the
older days, hour by hour for the last week. What needs the hour keeps silent; the rest works."""
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
import unittest
from zoneinfo import ZoneInfo

from replay import HOME, need
from engine import baseline, heating, report, tariff
from engine import home as H
from engine.sources import equipment, read_page
from replay import degree_days

PARIS = ZoneInfo("Europe/Paris")
START = datetime(2025, 11, 7, 8, tzinfo=timezone.utc)
STAT, STAT_SENT = "linky:12345678901234", "linky_prod:12345678901234"


@lru_cache(maxsize=1)
def linky_home():
    """Frank's own HA Linky statistics (installed on 7 Nov. 2026, read only): one value a day until 31 Oct., then
    the load curve by the hour; consumption and what was sent to the grid. Wh, read in kWh as the Recorder gives them."""
    import gzip
    import json
    raw = json.load(gzip.open(HOME / "ha-linky.json.gz", "rt"))

    def rows(prefix):
        sid = next(k for k in raw["lignes"] if k.split(":")[0] == prefix)
        return [{"start": datetime.fromtimestamp(r["start"] / 1000, timezone.utc), "sum": r["sum"], "mean": None,
                 "min": None, "max": None} for r in raw["lignes"][sid]]

    consumption, production = rows("linky"), rows("linky_prod")
    prefs = {"energy_sources": [{"type": "grid", "stat_energy_from": STAT, "stat_energy_to": STAT_SENT}]}
    home = H.build(read_page(prefs), {STAT: consumption, STAT_SENT: production}, PARIS, START, kva=9)
    cut = next(r["start"] for a, r in zip(consumption, consumption[1:]) if r["start"] - a["start"] == timedelta(hours=1))
    return home, cut


class HaLinkyOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        need(HOME / "ha-linky.json.gz")
        cls.home, cls.cut = linky_home()

    def test_level_0_and_not_hour_by_hour_from_the_page(self):
        level = equipment(read_page({"energy_sources": [{"type": "grid", "stat_energy_from": STAT}]}))
        self.assertEqual(level.level, 0)
        self.assertFalse(level.hourly)

    def test_the_days_are_whole(self):
        used = self.home.used_days()
        self.assertGreater(len(used), 340)
        self.assertEqual(self.cut.astimezone(PARIS).date(), date(2026, 10, 31))   # the load curve starts there

    def test_the_heating_from_the_cold_still_works(self):
        learned = heating.learn(self.home.used_days(), degree_days())
        self.assertTrue(learned.reliable)
        self.assertAlmostEqual(learned.per_degree_kwh, 1.67, delta=0.15)

    def test_the_night_baseload_waits_for_the_half_hours(self):
        self.assertIsNone(baseline.baseload(self.home.bought, PARIS))

    def test_an_old_day_has_no_hp_hc_price_a_recent_one_has(self):
        table = tariff.load_regulated()
        contract = tariff.Contract(tariff.HPHC, 9, tariff.parse_offpeak("0:14-8:19"))
        old = report.day(self.home, contract, table, date(2026, 10, 29))
        self.assertIsNone(old.energy_eur)                    # one value for the day: which part was off-peak is unknown
        recent = report.day(self.home, contract, table, self.cut.astimezone(PARIS).date() + timedelta(days=2))
        self.assertIsNotNone(recent.energy_eur)
        base = tariff.Contract(tariff.BASE, 9)
        self.assertIsNotNone(report.day(self.home, base, table, date(2026, 10, 29)).energy_eur)

    def test_the_typed_off_peak_hours(self):
        found = tariff.parse_offpeak("22h-6h, 12:30 - 14:30")
        self.assertEqual([r.label() for r in found.ranges], [("22 h", "6 h"), ("12 h 30", "14 h 30")])
        self.assertIsNone(tariff.parse_offpeak(""))


if __name__ == "__main__":
    unittest.main()


class HaLinkyReviewsAndDays(unittest.TestCase):
    """The rest of palier 0 on Frank's HA Linky statistics: the reviews and the unusual days, in kWh and in Base euros."""

    @classmethod
    def setUpClass(cls):
        need(HOME / "ha-linky.json.gz")
        cls.home, cls.cut = linky_home()

    def test_the_reviews_in_base(self):
        from engine import report as R
        found = {r["id"]: r for r in R.reviews(self.home, tariff.Contract(tariff.BASE, 9), tariff.load_regulated(),
                                               datetime(2026, 11, 7, 10, tzinfo=PARIS))}
        self.assertTrue(found["hier"]["titre"].startswith("Hier : "))
        self.assertTrue(found["mois"]["titre"].startswith("Octobre : "))
        self.assertNotIn("soleil", found["mois"]["texte"])      # no panels measured: nothing said of the sun

    def test_the_unusual_days(self):
        from engine import anomaly
        used, cold = self.home.used_days(), degree_days()
        learned = heating.learn(used, cold)
        found = [d for d in used if (u := anomaly.check(d, used, learned, cold)) is not None and u.more]
        self.assertIn(date(2025, 12, 24), found)
        self.assertLess(len(found), 25)


class EnedisAgainstTheHomesMeters(unittest.TestCase):
    """Enedis fait foi: Frank's page meters (Comwatt) against his HA Linky statistics, day by day."""

    def test_the_gap_and_the_days_off(self):
        from engine import health, stats
        from test_home import franks_home
        need(HOME / "ha-linky.json.gz")
        linky, _ = linky_home()
        home = franks_home()
        found = {f.id + ":" + f.values["quoi"]: f.values for f in
                 health.against_reference(STAT, "vos achats", stats.days(home.bought, PARIS), stats.days(linky.bought, PARIS))
                 + health.against_reference(STAT_SENT, "votre revente", stats.days(home.sent, PARIS), stats.days(linky.sent, PARIS))}
        self.assertEqual(found["p_reference_ecart:vos achats"]["sens"], "plus")          # Enedis counts more than Comwatt
        self.assertEqual(found["p_reference_ecart:vos achats"]["pourcent"], 4)
        self.assertEqual(found["p_reference_jours:vos achats"]["date"], date(2026, 2, 27))   # 0.5 kWh against 17
        self.assertEqual(found["p_reference_ecart:votre revente"]["sens"], "moins")        # Comwatt's resale too high

    def test_a_meter_a_thousand_times_off_is_not_compared(self):
        from engine import health, stats
        from test_home import franks_home
        need(HOME / "ha-linky.json.gz")
        linky, _ = linky_home()
        tiny = {d: stats.Total(t.kwh / 1000, t.unknown_hours, t.hours) for d, t in stats.days(linky.bought, PARIS).items()}
        self.assertEqual(health.against_reference(STAT, "vos achats", stats.days(franks_home().bought, PARIS), tiny), [])


class EuroFollowEnedis(unittest.TestCase):
    """Decided on 7 Nov. 2026: the euros follow Enedis. Frank's page meters set day by day on his HA Linky totals."""

    @classmethod
    def setUpClass(cls):
        from engine import home as H2
        from test_home import franks_home
        need(HOME / "ha-linky.json.gz")
        cls.linky, _ = linky_home()
        cls.page = franks_home()
        cls.followed = H2.follow(H2.follow(cls.page, "import", cls.linky.bought), "export", cls.linky.sent)

    def test_each_day_is_enedis_total(self):
        from engine import stats
        mine = stats.days(self.followed.bought, PARIS)
        enedis = stats.days(self.linky.bought, PARIS)
        for day in (date(2026, 1, 15), date(2026, 6, 15), date(2026, 10, 29)):
            self.assertAlmostEqual(mine[day].kwh, enedis[day].kwh, places=3)

    def test_the_missed_day_gets_enedis_total(self):
        from engine import stats
        self.assertAlmostEqual(stats.days(self.followed.bought, PARIS)[date(2026, 2, 27)].kwh, 17.0, delta=0.1)

    def test_the_year_and_the_euros(self):
        from engine import stats
        start, end = datetime(2025, 11, 8, tzinfo=PARIS), datetime(2026, 11, 1, tzinfo=PARIS)
        # Within 0.3 %: the days with hours the page lost (jumps set aside) keep their gaps, never invented.
        self.assertAlmostEqual(stats.total(self.followed.bought, start, end).kwh,
                               stats.total(self.linky.bought, start, end).kwh, delta=15)
        table = tariff.load_regulated()
        hp = next(r.series for r in self.page.of("import") if r.meter.period == "hp")
        hc = next(r.series for r in self.page.of("import") if r.meter.period == "hc")
        contract = tariff.Contract(tariff.HPHC, 9, tariff.learn_offpeak(hp, hc, PARIS))
        before = report.day(self.page, contract, table, date(2026, 10, 29)).energy_eur
        after = report.day(self.followed, contract, table, date(2026, 10, 29)).energy_eur
        self.assertAlmostEqual(before, 2.44, places=2)
        self.assertGreater(after, before)              # Enedis counted more that day


class AgainstFranksBill(unittest.TestCase):
    """Frank's EDF bill of 19 July 2026: its monthly readings (off-peak, peak) against what Hestia makes of his meters
    set on Enedis; and its subscriptions against the CRE's table."""

    def test_the_monthly_readings_within_3_percent(self):
        import json as j
        from engine import home as H2, stats
        from test_home import franks_home
        need(HOME / "facture-2026-07.json")
        bill = j.loads((HOME / "facture-2026-07.json").read_text(encoding="utf-8"))
        linky, _ = linky_home()
        followed = H2.follow(franks_home(), "import", linky.bought)
        for month, (hc, hp) in bill["releves_mensuels_kwh"].items():
            y, m = map(int, month.split("-"))
            a, b = datetime(y, m, 18, tzinfo=PARIS), datetime(y + m // 12, m % 12 + 1, 18, tzinfo=PARIS)
            got = {r.meter.period: stats.total(r.series, a, b).kwh for r in followed.of("import")}
            self.assertAlmostEqual(got["hc"] + got["hp"], hc + hp, delta=0.03 * (hc + hp) + 2, msg=month)
            self.assertAlmostEqual(got["hc"] / (got["hc"] + got["hp"]), hc / (hc + hp), delta=0.03, msg=month)

    def test_the_subscriptions_are_the_bill_s(self):
        import json as j
        need(HOME / "facture-2026-07.json")
        bill = j.loads((HOME / "facture-2026-07.json").read_text(encoding="utf-8"))
        table = tariff.load_regulated()
        for start, monthly in bill["abonnement_ht_mois"].items():
            grid = next(p for p in table["periodes"] if p["debut"] == start)
            self.assertAlmostEqual(grid["hphc"]["abonnement_an_ht"]["9"], monthly * 12, places=2)   # 169,68 € ; 176,16 €
        self.assertAlmostEqual(table["majoration_autoproducteur"][0]["ht_an"], bill["majoration_autoproducteur_ht_mois"] * 12)
