"""A year of Frank's real meters: hours, jumps, days, off-peak hours and euros (lots 1.3, 1.4, 2.1, 3.4, 4.2)."""
import csv
from datetime import date, datetime, timedelta, timezone
import unittest
from zoneinfo import ZoneInfo

from replay import LEVEL0, hourly, need
from engine import stats, tariff

PARIS = ZoneInfo("Europe/Paris")
HP, HC = "sensor.soutirrage_edf_kwh_energy_hp", "sensor.soutirrage_edf_kwh_energy_hc"
EXPORT = "sensor.echange_reseau_soutirage_injection_injection_total_energy"


def meters(limit=9.0):
    rows = hourly()
    return stats.energy(HP, rows[HP], limit), stats.energy(HC, rows[HC], limit)


class Jumps(unittest.TestCase):
    def test_the_twelve_jumps_of_summer_are_set_aside(self):
        # LISEZMOI says 13; the statistics hold 12: 10 on the peak meter, 2 on the off-peak one, all of 5 300 to 5 500 kWh.
        hp, hc = meters()
        self.assertEqual((len(hp.jumps), len(hc.jumps)), (10, 2))
        for jump in [*hp.jumps, *hc.jumps]:
            self.assertTrue(5300 < jump.kwh < 5500)
            self.assertIn(jump.start.astimezone(PARIS).month, (7, 8))

    def test_without_the_subscribed_power_the_meter_finds_them_alone(self):
        hp, hc = meters(limit=None)
        self.assertEqual((len(hp.jumps), len(hc.jumps)), (10, 2))

    def test_the_export_meter_of_the_cloud_steps_back(self):
        # Comwatt's export corrects itself: small steps back, read as zero. Its impossible hours need the sun
        # (test_home: no meter's own history can tell 20 kWh from a sunny hour caught up late).
        series = stats.energy(EXPORT, hourly()[EXPORT])
        self.assertGreater(series.backs, 0)


class Year(unittest.TestCase):
    def test_every_day_matches_the_level_0_file(self):
        need(LEVEL0)
        days = stats.days(stats.merge(*meters()), PARIS)
        with open(LEVEL0 / "achats-reseau-par-jour.csv", newline="") as f:
            reference = {date.fromisoformat(r["jour"]): float(r["kwh_achetes"]) for r in csv.DictReader(f)}
        apart = [d for d, kwh in reference.items() if d in days and abs(days[d].kwh - kwh) > 0.05]
        # 21 July: a jump hour of the peak meter also had 0.26 kWh off-peak; the hour is unknown as a whole.
        self.assertEqual(apart, [date(2026, 7, 21)])
        self.assertAlmostEqual(sum(t.kwh for t in days.values()), sum(reference.values()), delta=1)


class OffPeak(unittest.TestCase):
    def test_the_off_peak_hours_are_read_on_the_two_meters(self):
        hp, hc = meters()
        for end in (datetime(2026, 1, 15, tzinfo=timezone.utc), datetime(2026, 7, 15, tzinfo=timezone.utc), None):
            learned = tariff.learn_offpeak(hp, hc, PARIS, end)
            self.assertEqual(len(learned.ranges), 1)
            start, finish = learned.ranges[0].start, learned.ranges[0].end
            # About 0:10 to 8:10, eight hours, winter and summer alike.
            self.assertTrue(5 <= start <= 20, start)
            self.assertTrue(8 * 60 <= finish <= 8 * 60 + 25, finish)
            self.assertAlmostEqual(learned.ranges[0].minutes, 480, delta=15)

    def test_the_next_change_is_said_to_the_minute(self):
        learned = tariff.learn_offpeak(*meters(), PARIS)
        moment, period = tariff.next_change(learned, datetime(2026, 11, 7, 20, tzinfo=PARIS), PARIS)
        self.assertEqual(period, "hc")
        self.assertEqual((moment.date(), moment.hour), (date(2026, 11, 8), 0))


class Euros(unittest.TestCase):
    def setUp(self):
        self.table = tariff.load_regulated()
        hp, hc = meters()
        self.metered = [(hp, "hp"), (hc, "hc")]
        self.contract = tariff.Contract(tariff.HPHC, 9, tariff.learn_offpeak(hp, hc, PARIS))

    def test_the_29th_of_october(self):
        # A1: 7.87 kWh in peak hours, 4.75 off-peak, at 0.2142 and 0.1589 € (the regulated tariff since 1 August 2026).
        start, end = tariff.day_bounds(date(2026, 10, 29), PARIS)
        euros = tariff.cost(self.contract, self.table, PARIS, self.metered, start, end)
        self.assertTrue(euros.complete)
        self.assertAlmostEqual(euros.eur, 2.44, places=2)
        self.assertAlmostEqual(tariff.subscription(self.contract, self.table, date(2026, 10, 29)), 239.84 / 365)

    def test_november_2025_now_has_its_euros(self):
        # The CRE's grids since 2012 (data.gouv.fr): Frank's first months are priced, at the CRE's own subscriptions.
        start, end = datetime(2025, 11, 1, tzinfo=PARIS), datetime(2025, 12, 1, tzinfo=PARIS)
        euros = tariff.cost(self.contract, self.table, PARIS, self.metered, start, end)
        self.assertEqual(euros.unknown_kwh, 0)
        self.assertGreater(euros.eur, 150)
        self.assertAlmostEqual(tariff.subscription(self.contract, self.table, date(2025, 11, 1)), 239.84 / 365)
        self.assertAlmostEqual(tariff.subscription(self.contract, self.table, date(2026, 3, 1)), 235.92 / 365)

    def test_a_price_never_known_is_never_free(self):
        # Before the CRE's first grid (23 July 2012) the table knows nothing: no price, never a free kWh.
        self.assertIsNone(tariff.regulated_price(self.table, date(2012, 7, 1), tariff.HPHC, 9, "hp"))
        self.assertIsNone(tariff.subscription(tariff.Contract(tariff.HPHC, 9), self.table, date(2012, 7, 1)))

    def test_one_meter_is_split_by_the_learned_hours(self):
        # The same energy as one meter, as a plain Linky gives it: the learned hours split it almost like the two meters.
        start, end = datetime(2026, 10, 1, tzinfo=PARIS), datetime(2026, 11, 1, tzinfo=PARIS)
        two = tariff.cost(self.contract, self.table, PARIS, self.metered, start, end).eur
        one = tariff.cost(self.contract, self.table, PARIS, [(stats.merge(*[m for m, _ in self.metered]), None)], start, end).eur
        self.assertAlmostEqual(one, two, delta=two * 0.01)


if __name__ == "__main__":
    unittest.main()


class TempoDays(unittest.TestCase):
    """Tempo (3.1): each day's colour kept, the energy priced at that colour from the regulated table; a day without
    its colour has no price."""

    def test_a_colour_kept_for_days_counts_for_each(self):
        from custom_components.hestia_energy.reader import colours_by_day
        t = lambda d, h: datetime(2026, 11, d, h, tzinfo=PARIS)  # noqa: E731
        found = colours_by_day([(t(2, 6), "Bleu"), (t(4, 6), "BLANC"), (t(5, 6), "unknown")], t(6, 9))
        self.assertEqual(found, {date(2026, 11, 2): "bleu", date(2026, 11, 3): "bleu", date(2026, 11, 4): "blanc"})

    def test_the_regulated_tempo_prices(self):
        table = tariff.load_regulated()
        contract = tariff.Contract(tariff.TEMPO, 9, None, colors={date(2026, 10, 29): "rouge"})
        hp, hc = meters()
        start, end = tariff.day_bounds(date(2026, 10, 29), PARIS)
        start, end = start + timedelta(hours=6), end + timedelta(hours=6)
        red = tariff.cost(contract, table, PARIS, [(hp, "hp"), (hc, "hc")], start, end, contract.colors)
        self.assertGreater(red.eur, 0)
        none = tariff.cost(contract, table, PARIS, [(hp, "hp"), (hc, "hc")], start + timedelta(days=1), end + timedelta(days=1), contract.colors)
        self.assertEqual(none.eur, 0)
        self.assertGreater(none.unknown_kwh, 0)


class TodaysPricesAreNotHistory(unittest.TestCase):
    """Frank's page takes its prices from Tarif EDF: today's (0.2142 / 0.1589). They are the regulated ones, so the
    past keeps its own (November 2025: 0.2081 / 0.1635), never today's."""

    def test_regulated_prices_recognised(self):
        table = tariff.load_regulated()
        c = tariff.Contract(tariff.HPHC, 9, prices={"hp": 0.2142, "hc": 0.1589})
        self.assertTrue(tariff.regulated_today(c, table, date(2026, 11, 8)))
        self.assertFalse(tariff.regulated_today(c, table, date(2026, 3, 8)))        # not February's prices
        market = tariff.Contract(tariff.HPHC, 9, prices={"hp": 0.1990, "hc": 0.1490})
        self.assertFalse(tariff.regulated_today(market, table, date(2026, 11, 8)))   # a market offer keeps its own
