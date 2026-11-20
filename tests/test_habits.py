"""« Ton contrat, bien utilisé » (Frank, 19 Nov. 2026): the year's share of off-peak purchases, and for each device that
can wait, its energy in the sun, at night and in paid peak hours, with what moving the paid hours would save.
No real data needed: a made-up home of 120 days."""
from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest
from zoneinfo import ZoneInfo

from engine import habits, tariff
from engine.stats import Hour, Series

PARIS = ZoneInfo("Europe/Paris")
NOW = datetime(2026, 11, 19, 22, tzinfo=PARIS)
DAYS = 120


def home():
    """Sunny days (the first half): the sun covers the home from 11 h to 14 h; the water heater (2 kWh at 11 h) eats the
    whole surplus of 11 h, so nothing is sent then, and 1.5 kWh at 12 h and 13 h. Dark days: all from the grid."""
    start = (NOW - timedelta(days=DAYS)).replace(hour=0)
    hours = [start + timedelta(hours=k) for k in range(DAYS * 24)]
    sunny_day = lambda t: (t - start).days < DAYS // 2          # noqa: E731
    local = lambda t: t.astimezone(PARIS).hour                     # noqa: E731
    sunny = lambda t: sunny_day(t) and local(t) in (11, 12, 13)    # noqa: E731
    heater_kwh = lambda t: 2.0 if local(t) == 11 else 0.0          # noqa: E731
    washer_kwh = lambda t: 1.0 if local(t) == 20 and (t - start).days % 3 == 0 else 0.0  # noqa: E731
    bought = Series("sensor.achat", [Hour(t, 0.0 if sunny(t) else 0.5 + heater_kwh(t) + washer_kwh(t)) for t in hours])
    sent = Series("sensor.revente", [Hour(t, 1.5 if sunny(t) and local(t) != 11 else 0.0) for t in hours])
    heater = Series("sensor.chauffe_eau", [Hour(t, heater_kwh(t)) for t in hours])
    washer = Series("sensor.lave_linge", [Hour(t, washer_kwh(t)) for t in hours])
    fridge = Series("sensor.frigo", [Hour(t, 0.05) for t in hours])

    def reading(stat, name, series):
        return SimpleNamespace(meter=SimpleNamespace(stat=stat, name=name, included_in=None, kind="device"), series=series)
    devices = [reading("sensor.chauffe_eau", "Chauffe eau", heater), reading("sensor.lave_linge", "Lave linge ", washer),
               reading("sensor.frigo", "Frigo", fridge)]
    return SimpleNamespace(tz=PARIS, bought=bought, sent=sent, sun=None, metered=lambda: [(bought, None)],
                           of=lambda kind: devices if kind == "device" else [])


class Usage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = tariff.load_regulated()
        contract = tariff.Contract(tariff.HPHC, 9, tariff.parse_offpeak("0:13-8:20"), export_price=0.1276)
        cls.found = habits.usage(home(), contract, cls.table, NOW)

    def test_the_share_of_the_night(self):
        bought = home().bought.hours
        night = sum(h.kwh for h in bought if h.start.astimezone(PARIS).hour < 8)
        self.assertAlmostEqual(self.found["part_hc"], night / sum(h.kwh for h in bought), places=2)
        self.assertGreater(self.found["seuil_hc"], 0.1)
        self.assertIsNotNone(self.found["base_de_plus"])

    def test_the_water_heater_comes_first_and_the_sun_it_ate_counts(self):
        # At 11 h on sunny days nothing is sent: the heater took the whole surplus. Its sun is still the sun.
        heater = self.found["appareils"][0]
        self.assertEqual(heater["type"], "chauffe_eau")
        self.assertAlmostEqual(heater["soleil"], 0.5, places=2)
        self.assertAlmostEqual(heater["pleines"], 0.5, places=2)
        p = self.found["prix"]
        self.assertAlmostEqual(heater["euros_an"], heater["pleines_kwh"] * (p["hp"] - p["hc"]), places=1)
        self.assertGreater(self.found["part_hc_chauffe_eau"], self.found["part_hc"])

    def test_only_what_can_wait_and_names_trimmed(self):
        names = [d["nom"] for d in self.found["appareils"]]
        self.assertEqual(names, ["Chauffe eau", "Lave linge"])

    def test_days_with_sun_to_spare(self):
        months = self.found["soleil_mois"]
        self.assertTrue(months)
        self.assertEqual(sum(m["jours"] for m in months), DAYS // 2)

    def test_not_on_base(self):
        contract = tariff.Contract(tariff.BASE, 9)
        self.assertIsNone(habits.usage(home(), contract, self.table, NOW))


class Advices(unittest.TestCase):
    """« Pour économiser » as maquette D says it: what is done today, what would be better, the euros a year."""

    @classmethod
    def setUpClass(cls):
        table = tariff.load_regulated()
        cls.contract = tariff.Contract(tariff.HPHC, 9, tariff.parse_offpeak("0:13-8:20"), export_price=0.1276)
        cls.found = habits.usage(home(), cls.contract, table, NOW)
        cls.advices = {a["id"]: a for a in habits.advices(cls.found, cls.contract, sun=True)}

    def test_cycles_and_their_hour(self):
        heater, washer = self.found["appareils"]
        self.assertEqual((heater["cycles"], heater["depart"], heater["depart_part"], heater["duree"]), (DAYS, 11, 1.0, 1))
        self.assertEqual((washer["cycles"], washer["depart"], washer["prix_fort"]), (DAYS // 3, 20, 1.0))
        self.assertEqual(sum(sum(h) for h in heater["profil"]), 1.0)
        self.assertEqual(self.found["soleil_heures"], [12, 14])

    def test_the_months_the_sun_does_not_reach_the_heater(self):
        heater = self.found["appareils"][0]
        self.assertEqual(heater["mois_sans_soleil"], [10, 11])
        a = self.advices["chauffe_eau_heures"]
        self.assertEqual(a["maintenant"].split(".")[0], "Programmé à 11 h tous les jours")
        self.assertIn("D'octobre à novembre, programmez-le à 0 h 30. Remettez 11 h en décembre", a["mieux"])
        self.assertEqual(a["euros_an"], round(heater["euros_sans_soleil"]))
        self.assertEqual(a["mieux_heures"], [[0, 1, "hc"]])
        self.assertEqual((a["depart"], a["lancer"]), (11 * 60, 30))  # the pins of the card's strips

    def test_a_machine_at_the_dear_hour(self):
        a = self.advices["machine_heures"]
        self.assertEqual(a["nom"], "Lave linge")
        self.assertEqual(a["maintenant"], "Il tourne surtout vers 20 h : tous les lavages au prix fort.")
        self.assertEqual(a["mieux"], "Les jours de soleil, lancez-le entre 12 h et 14 h. Sinon, départ différé à 0 h 30.")
        self.assertTrue(a["sous"].startswith("par an, ") and a["sous"].endswith(" par lavage"))
        self.assertEqual((a["depart"], a["lancer"]), (20 * 60, 30))

    def test_without_panels_the_night_only(self):
        a = {x["id"]: x for x in habits.advices(self.found, self.contract, sun=False)}["machine_heures"]
        self.assertEqual(a["mieux"], "Départ différé à 0 h 30.")
        self.assertEqual(a["mieux_heures"], [[0, 1, "hc"]])

    def test_nothing_without_off_peak_hours(self):
        self.assertEqual(habits.advices(self.found, tariff.Contract(tariff.HPHC, 9), sun=True), [])
        self.assertEqual(habits.advices(None, self.contract, sun=True), [])

    def test_months_across_the_new_year(self):
        self.assertEqual(habits._months([11, 12, 1, 2]), (11, 2))
        self.assertIsNone(habits._months([1, 5]))


class Power(unittest.TestCase):
    """9 kVA: is 6 kVA enough? Each day's highest power bought over the year, a glitch above twice the kVA left out."""

    def rows(self, peaks):
        start = (NOW - timedelta(days=len(peaks))).replace(hour=12)
        return [{"start": (start + timedelta(days=k)).timestamp(), "max": w, "min": 0.0, "mean": w / 3}
                for k, w in enumerate(peaks)]

    def setUp(self):
        self.table = tariff.load_regulated()
        self.contract = tariff.Contract(tariff.HPHC, 9, tariff.parse_offpeak("0:13-8:20"))

    def test_days_above_the_power_just_below(self):
        peaks = [4000.0] * 300 + [7000.0] * 62 + [27753.0]
        found = habits.power([(self.rows(peaks), False)], self.contract, self.table, NOW, PARIS)
        self.assertEqual(found["plus_bas"]["kva"], 6)
        self.assertEqual(found["plus_bas"]["jours_au_dessus"], 62)
        self.assertEqual(found["pointe_w"], 7000)
        self.assertGreater(found["plus_bas"]["euros_an"], 20)

    def test_an_inverted_sensor_reads_its_lowest(self):
        rows = [{**r, "max": 0.0, "min": -r["max"]} for r in self.rows([4000.0] * 120)]
        found = habits.power([(rows, True)], self.contract, self.table, NOW, PARIS)
        self.assertEqual(found["plus_bas"]["jours_au_dessus"], 0)
        self.assertEqual(found["pointe_w"], 4000)

    def test_too_few_days(self):
        self.assertIsNone(habits.power([(self.rows([4000.0] * 30), False)], self.contract, self.table, NOW, PARIS))


if __name__ == "__main__":
    unittest.main()
