"""The panels' health (5.5) on Frank's real year: ten OpenDTU channels, no false alarm, a dead one found the same day."""
from datetime import datetime, timedelta, timezone
import unittest
from zoneinfo import ZoneInfo

from replay import hourly, need
from engine import solar

PARIS = ZoneInfo("Europe/Paris")


class Panels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        need()
        rows = hourly()
        cls.channels = {c: rows[c] for c in rows if c.endswith(("_ch1_power", "_ch2_power"))}
        cls.days = solar.channel_days(cls.channels, PARIS)

    def test_ten_channels_all_year(self):
        self.assertEqual(len(self.channels), 10)
        self.assertGreater(len(self.days), 350)

    def test_no_false_alarm_in_a_year(self):
        flagged = {d: solar.behind(self.days, d) for d in self.days}
        self.assertEqual({d: b for d, b in flagged.items() if b}, {})

    def test_a_dead_panel_is_found_the_same_day(self):
        """A real June day with one channel set to zero, as a broken connector would leave it."""
        day = max(d for d in self.days if d.month == 6 and sum(self.days[d].values()) > 10)
        broken = {**self.days, day: {**self.days[day], "sensor.sud_ch1_power": 0.0}}
        found = solar.behind(broken, day)
        self.assertEqual([b.channel for b in found], ["sensor.sud_ch1_power"])
        self.assertEqual(found[0].ratio, 0.0)

    def test_a_grey_day_says_nothing(self):
        grey = min(self.days, key=lambda d: sum(self.days[d].values()))
        self.assertEqual(solar.behind(self.days, grey), [])

    def test_the_panels_names(self):
        self.assertEqual(solar.panel_name("SUD-2 CH1 Power"), "Sud-2 · voie 1")
        self.assertEqual(solar.panel_name("Ouest-est CH2 Power"), "Ouest-est · voie 2")
        self.assertEqual(solar.panel_name("Garage"), "Garage")

    def test_the_silent_inverter(self):
        now = datetime(2026, 6, 15, 12, tzinfo=timezone.utc)
        self.assertEqual(solar.silent_minutes("unavailable", now - timedelta(minutes=45), now, True), 45)
        self.assertIsNone(solar.silent_minutes("unavailable", now - timedelta(hours=9), now, False))   # night
        self.assertIsNone(solar.silent_minutes("1234", now - timedelta(minutes=45), now, True))


if __name__ == "__main__":
    unittest.main()
