"""The live arbiter on a real snapshot of Frank's home (7 Nov. 2026, 13 h 15): A5 problems 2 and 5."""
from datetime import datetime, timedelta, timezone
import unittest

from replay import live_snapshot
from engine.live import Candidate, Flow, Reading, judge

NOW = datetime(2026, 11, 19, 19, 40, tzinfo=timezone.utc)


class Production(unittest.TestCase):
    def setUp(self):
        self.now, self.states = live_snapshot()

    def test_the_frozen_total_is_set_aside_for_opendtu(self):
        # A5, 2: « Total puissance produite instantanée » stuck at 0 W since 23 h 34 while the panels give 2 kW.
        frozen = Candidate("Total puissance produite", [(self.states["sensor.total_puissance_produite_instantanee_w"], 1)])
        opendtu = Candidate("OpenDTU", [(self.states["sensor.opendtu_8298a8_ac_power"], 1)], local=True)
        verdict = judge("production", [frozen, opendtu], self.now)
        self.assertIs(verdict.chosen, opendtu)
        self.assertAlmostEqual(verdict.value, 2083.1)
        reason = {c.name: why for c, why, _ in verdict.set_aside}
        self.assertEqual(reason["Total puissance produite"], "fige")

    def test_a_late_cloud_source_stays_behind_the_local_one(self):
        # A5, 5: three productions at the same moment; the Comwatt clamps are an hour late in their statistics.
        clamps = Candidate("Pinces Comwatt", [(self.states[e], 1) for e in ("sensor.panneaux_est", "sensor.panneaux_sud", "sensor.panneaux_ouest")
                                              if e in self.states], local=False, late=True)
        opendtu = Candidate("OpenDTU", [(self.states["sensor.opendtu_8298a8_ac_power"], 1)], local=True)
        verdict = judge("production", [clamps, opendtu], self.now)
        self.assertIs(verdict.chosen, opendtu)

    def test_a_silent_source_waits(self):
        opendtu = Candidate("OpenDTU", [(self.states["sensor.opendtu_8298a8_ac_power"], 1)], local=True)
        verdict = judge("production", [opendtu], self.now + timedelta(minutes=20))
        self.assertIsNone(verdict.chosen)
        self.assertEqual(verdict.set_aside[0][1], "muet")


class SumOfMeters(unittest.TestCase):
    """A source made of several meters (no real data needed: these run on GitHub too)."""

    def test_a_meter_at_rest_does_not_silence_the_sum(self):
        # Labo, 19 Nov. 2026: bought = peak-hours meter + off-peak meter. In peak hours the off-peak meter stays at 0 W
        # and reports nothing more; the peak-hours one reports every 15 s. The sum is alive.
        later = NOW + timedelta(minutes=20)
        peak = Reading("sensor.peak", "496", "W", later - timedelta(seconds=10), later - timedelta(seconds=10))
        rest = Reading("sensor.offpeak", "0", "W", NOW, NOW)
        verdict = judge("achat", [Candidate("Page Énergie", [(peak, 1), (rest, 1)])], later)
        self.assertEqual(verdict.value, 496)

    def test_a_working_meter_that_stops_still_silences_the_sum(self):
        later = NOW + timedelta(minutes=20)
        peak = Reading("sensor.peak", "496", "W", NOW, NOW)
        rest = Reading("sensor.offpeak", "0", "W", later, later)
        verdict = judge("achat", [Candidate("Page Énergie", [(peak, 1), (rest, 1)])], later)
        self.assertIsNone(verdict.chosen)
        self.assertEqual(verdict.set_aside[0][1], "muet")


class Water(unittest.TestCase):
    def test_a_flow_that_never_stops(self):
        now, _ = live_snapshot()
        flow = Flow()
        for minute in range(0, 45, 5):
            flow.update(0.4, now + timedelta(minutes=minute))
        self.assertEqual(flow.minutes(now + timedelta(minutes=45)), 45)
        self.assertAlmostEqual(flow.litres_per_day, 576)
        flow.update(0.0, now + timedelta(minutes=46))
        self.assertIsNone(flow.minutes(now + timedelta(minutes=46)))


if __name__ == "__main__":
    unittest.main()
