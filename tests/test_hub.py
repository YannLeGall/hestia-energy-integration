"""The Énergie tab of the hub (INTERFACE.md § 5): the devices' groups guessed from their names (H5), the comparison with
Enedis said in one source's card (H3), each finding attached to its meter (H6). Plain Python, Frank's real names."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from custom_components.hestia_energy.engine import hub, sources  # noqa: E402


class Groups(unittest.TestCase):
    def test_frank_s_devices_go_where_the_maquette_puts_them(self):
        cases = {"Chauffe eau": "eau_chaude", "Lave vaisselle": "cuisine_linge", "Sèche linge": "cuisine_linge",
                 "Plaque cuisson": "cuisine_linge", "Four": "cuisine_linge", "Frigo": "cuisine_linge", "Lave linge": "cuisine_linge",
                 "Chauffage Salon 1": "chauffage", "Sèche serviettes P": "chauffage", "Ordinateur": "reste",
                 "Domotique": "reste", "Prise aquarium": "reste", "Pompe piscine": "reste", "Imprimante 3D": "reste"}
        for name, group in cases.items():
            self.assertEqual(hub.guess_group(name), group, name)

    def test_a_device_without_a_name_is_guessed_from_its_entity(self):
        self.assertEqual(hub.guess_group(None, "sensor.fil_pilote_s1_energy"), "chauffage")
        self.assertEqual(hub.device_id("sensor.chauffe_eau_total_energy"), "chauffe_eau_total_energy")


class Findings(unittest.TestCase):
    def setUp(self):
        self.page = sources.read_page({"energy_sources": [{"type": "grid", "stat_energy_from": "sensor.achat",
                                                           "power_config": {"stat_rate": "sensor.achat_w"}}],
                                       "device_consumption": [{"stat_consumption": "sensor.frigo_kwh", "stat_rate": "sensor.frigo_w"}]})

    def test_a_frozen_power_belongs_to_its_meter(self):
        found = hub.by_meter([{"id": "p_capteur_fige", "stat": "sensor.frigo_w"}, {"id": "p_compteur_saut", "stat": "sensor.achat"},
                              {"id": "p_soleil_manquant", "stat": ""}], self.page)
        self.assertEqual(set(found), {"sensor.frigo_kwh", "sensor.achat"})

    def test_enedis_said_for_one_source(self):
        lines = hub.enedis_lines([
            {"id": "p_reference_ecart", "valeurs": {"quoi": "vos achats", "pourcent": 4, "sens": "plus", "jours": 354}},
            {"id": "p_reference_jours", "valeurs": {"quoi": "vos achats", "jours": 4, "date": "2026-02-27", "page": 0.5, "enedis": 17.0}},
            {"id": "p_reference_ecart", "valeurs": {"quoi": "votre revente", "pourcent": 5, "sens": "moins", "jours": 341}},
        ], "vos achats")
        self.assertEqual([x["titre"] for x in lines], ["Enedis compte 4 % de plus que vos compteurs", "4 jours nettement différents"])
        self.assertEqual(lines[1]["texte"], "Dont le 27 février 2026 : 0,5 kWh contre 17.")


if __name__ == "__main__":
    unittest.main()
