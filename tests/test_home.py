"""Frank's whole home over a year, every meter read with its own limit: the defects of A5 come out by themselves."""
from datetime import date, datetime, timezone
from functools import lru_cache
import unittest
from zoneinfo import ZoneInfo

from replay import description, hourly
from engine import home as H
from engine.sources import read_page

PARIS = ZoneInfo("Europe/Paris")
START = datetime(2025, 11, 7, 8, tzinfo=timezone.utc)


@lru_cache(maxsize=1)
def franks_home():
    rows = hourly()
    channels = sorted(k for k in rows if k.endswith(("_ch1_power", "_ch2_power")))
    return H.build(read_page(description()["page_energie"]), rows, PARIS, START, kva=9, inverters=channels)


def found(kind, stat=None):
    return [f for f in franks_home().findings if f.id == kind and (stat is None or f.stat == stat)]


class Defects(unittest.TestCase):
    def test_the_washing_machine_counted_in_wh_is_brought_to_kwh(self):
        # A5, 9: « lave-linge compté en Wh ».
        self.assertEqual(found("p_unite")[0].values, {"capteur": "Lave linge", "facteur": 1000})
        washer = franks_home().readings["sensor.lave_linge_total_energy"]
        self.assertLess(sum(h.kwh for h in washer.series.known()), 400)

    def test_the_cloud_devices_come_an_hour_late(self):
        late = {f.values["source"] for f in found("p_cloud_retard")}
        self.assertTrue({"Lave vaisselle", "Lave linge", "Four"} <= late)
        # LiXee is local: its meters are on time.
        self.assertNotIn("Soutirrage EDF HP", late)

    def test_the_grid_jumps_are_said_once_per_meter(self):
        jumps = {f.values["capteur"]: f.values["fois"] for f in found("p_compteur_saut")}
        self.assertEqual((jumps["Soutirrage EDF HP"], jumps["Soutirrage EDF HC"]), (10, 2))

    def test_the_export_jumps_of_summer_are_set_aside_by_the_sun(self):
        # 12 to 24 kWh in one hour from 5 kWc of panels (July, August).
        export = franks_home().readings["sensor.echange_reseau_soutirage_injection_injection_total_energy"]
        big = [j for j in export.series.jumps if j.kwh > 11]
        self.assertGreaterEqual(len(big), 20)
        self.assertTrue(all(j.start.astimezone(PARIS).month in (7, 8, 9) for j in big))

    def test_younger_meters_say_since_when(self):
        since = {f.values["capteur"]: f.values["date"] for f in found("p_depuis")}
        self.assertEqual(since["Consommation Poêle"], date(2026, 8, 25))
        self.assertEqual(since["Prise Buanderie Ext"], date(2026, 4, 20))

    def test_the_stove_and_the_power_without_statistics(self):
        self.assertEqual(len(found("p_fausse_source")), 2)
        self.assertEqual([f.values["nom"] for f in found("p_sans_statistiques")], ["Prise aquarium"])


class Sun(unittest.TestCase):
    def test_hours_the_page_missed_are_taken_from_the_inverters(self):
        self.assertGreater(found("p_soleil_onduleurs")[0].values["heures"], 0)

    def test_hours_nobody_measured_are_unknown_not_zero(self):
        # 11 to 18 March 2026: OpenDTU silent, the page at zero, yet 1.7 kW sent to the grid at 15 h.
        missing = found("p_soleil_manquant")[0].values["liste"]
        self.assertTrue({date(2026, 3, 13), date(2026, 3, 14), date(2026, 3, 15)} <= set(missing))
        day = franks_home().consumption_days()[date(2026, 3, 13)]
        self.assertFalse(day.complete)


class Whole(unittest.TestCase):
    def test_the_devices_never_exceed_the_home_but_on_a_rare_day(self):
        impossible = found("p_somme_impossible")
        self.assertLessEqual(impossible[0].values["jours"] if impossible else 0, 3)

    def test_the_year(self):
        home = franks_home()
        bought = sum(h.kwh for h in home.bought.known())
        self.assertAlmostEqual(bought, 5280, delta=5)
        days = home.consumption_days()
        self.assertGreater(sum(1 for t in days.values() if t.complete), 280)


if __name__ == "__main__":
    unittest.main()
