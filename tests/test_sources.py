"""The Energy page of Frank's real home, read in its 2026 format and in the former one (lot 1.1, 1.5)."""
import copy
import unittest

from replay import description
from engine.sources import FORMAT_2026, FORMAT_OLD, equipment, read_page


def former_format(prefs):
    """The same real page as Home Assistant wrote it before 2026: one grid source with flow_from and flow_to."""
    prefs = copy.deepcopy(prefs)
    grids = [s for s in prefs["energy_sources"] if s["type"] == "grid"]
    flow_from = [{"stat_energy_from": g["stat_energy_from"], "stat_cost": g.get("stat_cost"), "name": g.get("name"),
                  "entity_energy_price": g.get("entity_energy_price"), "number_energy_price": g.get("number_energy_price")}
                 for g in grids if g.get("stat_energy_from")]
    flow_to = [{"stat_energy_to": g["stat_energy_to"], "stat_compensation": g.get("stat_compensation"),
                "entity_energy_price": g.get("entity_energy_price_export"), "number_energy_price": g.get("number_energy_price_export")}
               for g in grids if g.get("stat_energy_to")]
    others = [s for s in prefs["energy_sources"] if s["type"] != "grid"]
    prefs["energy_sources"] = [{"type": "grid", "flow_from": flow_from, "flow_to": flow_to, "cost_adjustment_day": 0}, *others]
    return prefs


class FranksPage(unittest.TestCase):
    def setUp(self):
        self.prefs = description()["page_energie"]
        self.page = read_page(self.prefs)

    def test_the_2026_format_is_read(self):
        page = self.page
        self.assertEqual(page.format, FORMAT_2026)
        self.assertEqual([(m.stat, m.period) for m in page.imports],
                         [("sensor.soutirrage_edf_kwh_energy_hp", "hp"), ("sensor.soutirrage_edf_kwh_energy_hc", "hc")])
        self.assertEqual(page.imports[0].price.entity, "sensor.tarif_heures_pleines_ttc")
        self.assertEqual([m.stat for m in page.exports], ["sensor.echange_reseau_soutirage_injection_injection_total_energy"])
        self.assertEqual(page.exports[0].price.number, 0.1276)
        self.assertTrue(page.exports[0].power.inverted)
        self.assertEqual(len(page.solar), 3)
        self.assertEqual(len(page.devices), 23)
        self.assertEqual(page.water[0].price.number, 3.33)

    def test_the_stove_declared_as_gas_is_pointed_out(self):
        # A5 problem 7: the stove is declared twice as « gas », once by its electric plug.
        flagged = [r.values["stat"] for r in self.page.remarks if r.id == "p_fausse_source"]
        self.assertEqual(flagged, ["sensor.poele_energie", "sensor.prise_poele_energy"])

    def test_the_former_format_reads_the_same(self):
        old = read_page(former_format(self.prefs))
        self.assertEqual(old.format, FORMAT_OLD)
        for kind in ("imports", "exports", "solar", "gas", "water", "devices"):
            self.assertEqual([(m.stat, m.period, m.price.entity, m.price.number) for m in getattr(old, kind)],
                             [(m.stat, m.period, m.price.entity, m.price.number) for m in getattr(self.page, kind)], kind)

    def test_franks_home_is_level_3_hour_by_hour(self):
        level = equipment(self.page, description()["statistiques"])
        self.assertEqual((level.level, level.bill, level.live, level.devices, level.sun, level.hourly), (3, True, True, True, True, True))
        self.assertEqual(level.missing, ())

    def test_without_the_page_nothing_is_invented(self):
        page = read_page(None)
        self.assertTrue(page.empty)
        level = equipment(page)
        self.assertEqual((level.level, level.bill), (0, False))
        self.assertEqual(level.missing, ("compteur", "direct", "appareils", "soleil"))


if __name__ == "__main__":
    unittest.main()


class SourceKind(unittest.TestCase):
    def test_source_of_each_official_path(self):
        """D21: the consumption source is recognised by its statistic, its integration or its device."""
        from engine.sources import HA_LINKY, MYELECTRICALDATA, OTHER, TIC, source_of
        self.assertEqual(source_of("linky:12345678901234"), HA_LINKY)
        self.assertEqual(source_of("myelectricaldata:12345678901234_consumption"), MYELECTRICALDATA)
        self.assertEqual(source_of("sensor.consommation", "myelectricaldata"), MYELECTRICALDATA)
        self.assertEqual(source_of("sensor.zlinky_energie", "mqtt", "LiXee Lixee ZLinky"), TIC)
        self.assertEqual(source_of("sensor.index_base", "linkytic"), TIC)
        # Frank's own: templates attached to the Comwatt device, the LiXee read apart (live period).
        self.assertEqual(source_of("sensor.soutirrage_edf_kwh_energy_hp", "template", "Comwatt WITHDRAWAL"), OTHER)
