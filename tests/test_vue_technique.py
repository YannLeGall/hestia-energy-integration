"""The hub's technical overview (Frank, 20 Nov. 2026): when each source last spoke, and what Énergie can work out."""
from datetime import timedelta
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from homeassistant.util import dt as dt_util

    from custom_components.hestia_energy import hub_view  # noqa: E402
    from custom_components.hestia_energy.engine.rows import Rows  # noqa: E402
except ImportError:          # Home Assistant absent: tested on GitHub
    hub_view = None


def state(value: str, ago: timedelta):
    at = dt_util.utcnow() - ago
    return SimpleNamespace(state=value, last_reported=at, last_updated=at)


@unittest.skipIf(hub_view is None, "Home Assistant absent")
class Freshness(unittest.TestCase):
    def setUp(self):
        self.states = {}
        self.hass = SimpleNamespace(states=SimpleNamespace(get=self.states.get))
        self.c = SimpleNamespace(rows={})

    def test_a_meter_that_reported_a_minute_ago(self):
        self.states["sensor.linky"] = state("1234", timedelta(minutes=1))
        self.assertEqual(hub_view.freshness(self.hass, self.c, ["sensor.linky"])["etat"], "ok")

    def test_the_freshest_entity_of_the_source_counts(self):
        self.states["sensor.total"] = state("12", timedelta(hours=9))
        self.states["sensor.puissance"] = state("800", timedelta(seconds=8))
        self.assertEqual(hub_view.freshness(self.hass, self.c, ["sensor.total", "sensor.puissance"])["etat"], "ok")

    def test_silent_for_hours_is_late(self):
        self.states["sensor.panneaux"] = state("40", timedelta(hours=7))
        self.assertEqual(hub_view.freshness(self.hass, self.c, ["sensor.panneaux"])["etat"], "retard")

    def test_every_entity_unavailable_is_mute(self):
        self.states["sensor.panneaux"] = state("unavailable", timedelta(minutes=1))
        self.assertEqual(hub_view.freshness(self.hass, self.c, ["sensor.panneaux"]),
                         {"etat": "muet", "vu": None})

    def test_enedis_the_next_day_is_on_time(self):
        last = (dt_util.utcnow() - timedelta(hours=30)).replace(minute=0, second=0, microsecond=0)
        self.c.rows["linky:123"] = Rows.of([{"start": last, "sum": 10.0}])
        self.assertEqual(hub_view.freshness(self.hass, self.c, ["linky:123"])["etat"], "ok")

    def test_enedis_four_days_old_is_late(self):
        last = dt_util.utcnow() - timedelta(days=4)
        self.c.rows["linky:123"] = Rows.of([{"start": last, "sum": 10.0}])
        self.assertEqual(hub_view.freshness(self.hass, self.c, ["linky:123"])["etat"], "retard")


if __name__ == "__main__":
    unittest.main()
