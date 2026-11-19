"""« Un compteur compte double » (Frank's home, 19 Nov. 2026: the message said neither which day nor which meter, and
led to the very page it was on). Now: the last such day in figures, the pair declared twice or the heaviest devices,
and a link to the page Énergie of Home Assistant where it is mended."""
from datetime import date
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from custom_components.hestia_energy.engine import health  # noqa: E402

D1, D2 = date(2026, 11, 12), date(2026, 11, 14)


class Twins(unittest.TestCase):
    def test_two_devices_that_count_the_same_energy(self):
        per = {"sensor.prise_tv": {D1: 2.1, D2: 1.9}, "sensor.tv": {D1: 2.0, D2: 2.0}, "sensor.frigo": {D1: 1.2, D2: 1.1}}
        self.assertEqual(health.twins(per, [D1, D2]), ("sensor.prise_tv", "sensor.tv"))

    def test_close_one_day_only_is_not_a_pair(self):
        per = {"sensor.a": {D1: 2.0, D2: 0.5}, "sensor.b": {D1: 2.0, D2: 3.0}}
        self.assertIsNone(health.twins(per, [D1, D2]))

    def test_two_devices_at_rest_are_not_a_pair(self):
        per = {"sensor.a": {D1: 0.05, D2: 0.05}, "sensor.b": {D1: 0.05, D2: 0.05}}
        self.assertIsNone(health.twins(per, [D1, D2]))


class Recent(unittest.TestCase):
    """Only a double count that lasts is said: 3 days at least among the last 30."""

    def home(self, impossible_days):
        from datetime import timedelta
        from custom_components.hestia_energy.engine import home as home_mod
        end = date(2026, 11, 18)
        whole = {end - timedelta(days=k): 10.0 for k in range(200)}
        devices = {d: (12.0 if d in impossible_days else 6.0) for d in whole}
        found = []
        h = SimpleNamespace(consumption_days=lambda: {d: SimpleNamespace(kwh=v, complete=True) for d, v in whole.items()},
                            of=lambda kind: [], tz=None, findings=found)
        orig = health.impossible
        health.impossible = lambda w, dev: sorted(impossible_days)
        try:
            home_mod._impossible(h)
        finally:
            health.impossible = orig
        return found

    def test_two_days_long_ago_are_a_meter_s_history(self):
        self.assertEqual(self.home([date(2026, 5, 12), date(2026, 8, 23)]), [])

    def test_three_recent_days_are_said(self):
        found = self.home([date(2026, 11, 1), date(2026, 11, 8), date(2026, 11, 15)])
        self.assertEqual(found[0].id, "p_somme_impossible")
        self.assertEqual(found[0].values["jours"], 3)


try:
    from custom_components.hestia_energy import hub_view  # noqa: E402
except ImportError:          # Home Assistant absent: the sentence is tested on GitHub
    hub_view = None


@unittest.skipIf(hub_view is None, "Home Assistant absent")
class Sentence(unittest.TestCase):
    def setUp(self):
        self.hass = SimpleNamespace(states=SimpleNamespace(get=lambda e: None))
        self.c = SimpleNamespace(page=None, device_names={"sensor.prise_tv": "Prise TV", "sensor.tv": "Télévision",
                                                           "sensor.ordi": "Ordinateur", "sensor.domotique": "Domotique"})

    def test_a_pair_declared_twice(self):
        todo = hub_view._double(self.hass, self.c, {"jours": 2, "dernier": "2026-11-14", "maison_kwh": 9.4, "appareils_kwh": 11.2,
                                                    "doublon": ["sensor.prise_tv", "sensor.tv"], "plus_gros": ["sensor.tv"]})
        self.assertEqual(todo["page"], "ha")
        self.assertEqual(todo["sur"], "appareils")
        self.assertTrue(todo["texte"].startswith("Le 14 novembre, les appareils mesurés ont compté 11,2 kWh pour une maison à 9,4 kWh (2 jours en tout)."))
        self.assertIn("Prise TV et Télévision comptent presque pareil", todo["texte"])

    def test_without_a_pair_the_heaviest_devices(self):
        todo = hub_view._double(self.hass, self.c, {"jours": 1, "dernier": "2026-11-01", "maison_kwh": 9.4, "appareils_kwh": 11.2,
                                                    "doublon": None, "plus_gros": ["sensor.domotique", "sensor.ordi"]})
        self.assertIn("Le 1er novembre", todo["texte"])
        self.assertIn("À regarder d'abord : Domotique ou Ordinateur.", todo["texte"])
        self.assertIn("« Consommation en amont »", todo["texte"])

    def test_an_older_finding_without_figures(self):
        todo = hub_view._double(self.hass, self.c, {"jours": 2, "dernier": "2026-11-14"})
        self.assertIn("ont dépassé la maison entière (2 jours en tout)", todo["texte"])


if __name__ == "__main__":
    unittest.main()
