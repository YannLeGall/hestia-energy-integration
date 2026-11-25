"""A home heated with gas: its electricity says little about the cold, its gas meters say it. An invented home (no
gas home in the replay data): a year of degree-days, a boiler that burns 0.14 m³ for each of them and about 0.6 m³ a
day for the hot water, on an Energy page that counts the heating and the hot water on two gas meters, in m³."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import math
import unittest
from zoneinfo import ZoneInfo

from replay import ROOT  # noqa: F401 - puts the engine on the path
from engine import cards, gas, heating, stats
from engine.home import Reading
from engine.sources import GAS_ENERGY, GAS_VOLUME, Meter, Price, gas_unit

PARIS = ZoneInfo("Europe/Paris")
NOW = datetime(2026, 11, 25, 14, tzinfo=PARIS)
FIRST = date(2025, 11, 26)
PER_DEGREE, HOT_WATER, PRICE = 0.14, 0.6, 1.25      # m³ a degree-day, m³ a day, € a m³
HEATING, WATER = "sensor.gaz_chauffage", "sensor.gaz_eau_chaude"


def days() -> list[date]:
    return [FIRST + timedelta(days=i) for i in range((NOW.date() - FIRST).days + 1)]


def degree_days() -> dict[date, float]:
    """A year's cold: about 17 degree-days in mid-January, none in summer, never the same two days running."""
    out = {}
    for d in days():
        n = d.timetuple().tm_yday
        out[d] = round(max(0.0, 8 + 9 * math.cos(2 * math.pi * (n - 15) / 365) + 2 * math.sin(n * 1.7)), 1)
    return out


def series(stat: str, m3_of) -> stats.Series:
    """The meter hour by hour, in litres as the statistics are read; `m3_of(day)`: what it counts that day."""
    out = stats.Series(stat)
    at = datetime.combine(FIRST, datetime.min.time(), PARIS).astimezone(timezone.utc)
    while at < NOW:
        out.hours.append(stats.Hour(at, m3_of(at.astimezone(PARIS).date()) * 1000 / 24))
        at += timedelta(hours=1)
    return out


def reading(stat: str, name: str, m3_of) -> Reading:
    return Reading(Meter("gas", stat, name, Price(entity="sensor.gaz_prix_m3")), series(stat, m3_of))


class Invented:
    """The invented home and its season, for each class of tests."""

    @classmethod
    def setUpClass(cls):
        cls.cold = degree_days()
        wobble = lambda d: 0.05 * math.sin(d.toordinal() * 0.9)     # noqa: E731 - showers are not the same every day
        cls.readings = [reading(HEATING, "Chauffage", lambda d: PER_DEGREE * cls.cold[d]),
                        reading(WATER, "Eau chaude", lambda d: HOT_WATER + wobble(d))]
        cls.units = {HEATING: GAS_VOLUME, WATER: GAS_VOLUME}
        cls.prices = {HEATING: PRICE, WATER: PRICE}

    def season(self, **changes) -> dict | None:
        args = {"readings": self.readings, "units": self.units, "prices": self.prices, "cold": self.cold, "no_cold": None,
                "now": NOW, **changes}
        return cards.gas_season(**args)


class GasHome(Invented, unittest.TestCase):
    def test_the_gas_follows_the_cold(self):
        gas = self.season()
        self.assertEqual(gas["etat"], "pret")
        self.assertEqual(gas["unite"], "m³")
        self.assertAlmostEqual(gas["par_degre"], PER_DEGREE, delta=0.005)
        self.assertAlmostEqual(gas["reste_par_jour"], HOT_WATER, delta=0.05)
        self.assertAlmostEqual(gas["euros_par_degre"], PER_DEGREE * PRICE, delta=0.01)

    def test_the_season_and_the_heating_in_it(self):
        gas = self.season()
        season = gas["saison"]
        self.assertEqual(season["du"], "2026-10-01")
        since = [d for d in days() if d >= date(2026, 10, 1)]
        heat = sum(PER_DEGREE * self.cold[d] for d in since[:-1]) + PER_DEGREE * self.cold[NOW.date()] * 14 / 24
        water = HOT_WATER * (len(since) - 1 + 14 / 24)
        self.assertAlmostEqual(season["total"], heat + water, delta=0.5)
        self.assertAlmostEqual(season["eur"], season["total"] * PRICE, delta=0.1)
        # The heating: the gas beyond the home's summer level, close to what the heating meter counted.
        self.assertAlmostEqual(season["chauffage"], heat, delta=0.05 * heat)
        self.assertLess(season["chauffage"], season["total"])
        self.assertAlmostEqual(season["chauffage_eur"], season["chauffage"] * PRICE, delta=0.1)
        self.assertLessEqual(gas["mois"]["total"], season["total"])
        self.assertEqual(gas["mois"]["jours"], 25)

    def test_one_meter_counts_the_same(self):
        both = lambda d: PER_DEGREE * self.cold[d] + HOT_WATER      # noqa: E731
        one = self.season(readings=[reading(HEATING, "Gaz", both)], units={HEATING: GAS_VOLUME}, prices={HEATING: PRICE})
        self.assertEqual(one["etat"], "pret")
        self.assertAlmostEqual(one["saison"]["total"], self.season()["saison"]["total"], delta=1)

    def test_a_meter_in_kwh_keeps_its_unit(self):
        kwh = [Reading(r.meter, stats.Series(r.series.stat, [stats.Hour(h.start, h.kwh / 1000 * 11.2) for h in r.series.hours]))
               for r in self.readings]
        gas = self.season(readings=kwh, units={HEATING: GAS_ENERGY, WATER: GAS_ENERGY}, prices={HEATING: 0.11, WATER: 0.11})
        self.assertEqual(gas["unite"], "kWh")
        self.assertAlmostEqual(gas["par_degre"], PER_DEGREE * 11.2, delta=0.06)
        self.assertAlmostEqual(gas["saison"]["total"], self.season()["saison"]["total"] * 11.2, delta=1)

    def test_kwh_and_cubic_metres_are_never_added_up(self):
        self.assertIsNone(self.season(units={HEATING: GAS_VOLUME, WATER: GAS_ENERGY}))
        self.assertIsNone(self.season(units={}))
        self.assertIsNone(self.season(readings=[]))

    def test_without_a_price_no_euros(self):
        gas = self.season(prices={HEATING: PRICE})
        self.assertIsNone(gas["prix"])
        self.assertIsNone(gas["saison"]["eur"])
        self.assertIsNone(gas["saison"]["chauffage_eur"])
        self.assertIsNotNone(gas["saison"]["chauffage"])

    def test_without_the_cold_the_gas_is_counted_not_split(self):
        gas = self.season(no_cold="sans_meteo")
        self.assertEqual(gas["etat"], "sans_meteo")
        self.assertIsNotNone(gas["saison"]["eur"])
        self.assertIsNone(gas["saison"]["chauffage"])

    def test_a_few_weeks_are_not_enough(self):
        recent = {d: v for d, v in self.cold.items() if d >= date(2026, 11, 1)}
        gas = self.season(cold=recent)
        self.assertEqual(gas["etat"], "apprend")
        self.assertEqual(gas["jours"], 24)       # the whole days of November, not today
        self.assertIsNone(gas["saison"]["chauffage"])

    def test_gas_for_the_hot_water_only_is_not_heating(self):
        """A gas water heater in a home heated otherwise: the gas does not follow the cold, no heating is said."""
        gas = self.season(readings=[self.readings[1]], units={WATER: GAS_VOLUME}, prices={WATER: PRICE})
        self.assertEqual(gas["etat"], "peu_lie")
        self.assertIsNone(gas["saison"]["chauffage"])
        self.assertGreater(gas["saison"]["total"], 30)

    def test_a_meter_added_this_month_does_not_start_the_learning_again(self):
        """The hot water counted apart since 4 November only: before, that meter was not there, and nothing is missing."""
        late = Reading(self.readings[1].meter, stats.Series(WATER, [h for h in self.readings[1].series.hours
                                                                      if h.start >= datetime(2026, 11, 4, tzinfo=PARIS)]))
        gas = self.season(readings=[self.readings[0], late])
        self.assertEqual(gas["etat"], "pret")
        self.assertAlmostEqual(gas["par_degre"], PER_DEGREE, delta=0.005)

    def test_gas_counted_the_day_after_is_read_three_days_together(self):
        """A meter read late two days out of three (most of the day's gas lands on the next day): day by day the cold
        explains little, three days together it does, with the same slope."""
        true = {d: PER_DEGREE * self.cold[d] + HOT_WATER for d in days()}
        burnt = dict(true)
        for d in days()[:-1]:
            if d.toordinal() % 3:
                burnt[d] -= 0.9 * true[d]
                burnt[d + timedelta(days=1)] += 0.9 * true[d]
        by_day = heating.learn(burnt, self.cold)
        together = heating.learn(burnt, self.cold, heating.GAS_SPAN)
        self.assertFalse(by_day.reliable)
        self.assertTrue(together.reliable)
        self.assertAlmostEqual(together.per_degree_kwh, PER_DEGREE, delta=0.02)
        self.assertEqual(together.days % heating.GAS_SPAN, 0)

    def test_one_day_at_a_time_reads_as_before(self):
        burnt = {d: PER_DEGREE * self.cold[d] + HOT_WATER for d in days()}
        self.assertEqual(heating.learn(burnt, self.cold), heating.learn(burnt, self.cold, 1))
        self.assertEqual(heating.learn(burnt, self.cold).days, len(burnt))

    def test_never_more_heating_than_gas_burnt(self):
        """A week away in January, the boiler off: no gas, no heating, however cold it was."""
        away = {date(2026, 1, 10) + timedelta(days=i) for i in range(7)}
        burnt = {d: 0.0 if d in away else PER_DEGREE * self.cold[d] + HOT_WATER for d in days()}
        rest = heating.without_heating(burnt, self.cold, heating.learn(burnt, self.cold, heating.GAS_SPAN))
        self.assertAlmostEqual(rest, HOT_WATER, delta=0.05)
        week = heating.gas_over(burnt, rest, min(away), max(away), PRICE)
        self.assertEqual(week.as_dict(), {"total": 0.0, "eur": 0.0, "chauffage": 0.0, "chauffage_eur": 0.0, "jours": 7})
        self.assertIsNone(heating.gas_over(burnt, rest, date(2027, 1, 1), date(2027, 1, 31), PRICE))

    def test_a_mild_month_with_the_boiler_off_shows_no_heating(self):
        """October without heating although its days were a little cold: the gas is the hot water's, and the cold
        alone must not invent a heating (on a real gas home it gave more heating than all the gas burnt)."""
        october = [d for d in days() if d.year == 2026 and d.month == 10]
        burnt = {d: HOT_WATER if d in october else PER_DEGREE * self.cold[d] + HOT_WATER for d in days()}
        learned = heating.learn(burnt, self.cold, heating.GAS_SPAN)
        self.assertTrue(learned.reliable)
        self.assertGreater(sum(self.cold[d] for d in october), 100)
        # The summer says what the home burns without heating; the line alone would say less (it leans down).
        rest = heating.without_heating(burnt, self.cold, learned)
        self.assertAlmostEqual(rest, HOT_WATER, delta=0.05)
        self.assertLess(learned.rest_kwh, HOT_WATER - 0.05)
        month = heating.gas_over(burnt, rest, october[0], october[-1], PRICE)
        self.assertAlmostEqual(month.total, HOT_WATER * 31, places=6)
        self.assertAlmostEqual(month.heat, 0.0, places=6)

    def test_before_the_first_summer_the_line_says_the_rest(self):
        """A meter that has only known a winter: no day without cold yet, the line's level at no cold is taken."""
        winter = {d: PER_DEGREE * self.cold[d] + HOT_WATER for d in days() if d < date(2026, 3, 15)}
        learned = heating.learn(winter, self.cold, heating.GAS_SPAN)
        self.assertLess(sum(1 for d in winter if self.cold[d] <= heating.NO_COLD), heating.MIN_WARM_DAYS)
        self.assertAlmostEqual(heating.without_heating(winter, self.cold, learned), HOT_WATER, delta=0.02)
        self.assertIsNone(heating.without_heating(winter, self.cold, None))


class WhatHeats(Invented, unittest.TestCase):
    """Said in Réglages, the household's word comes before what the cold shows."""

    def test_not_said_the_gas_that_follows_the_cold_heats(self):
        self.assertTrue(self.season()["chauffe"])
        self.assertTrue(self.season(no_cold="sans_meteo")["chauffe"])     # it still may
        water_only = {"readings": [self.readings[1]], "units": {WATER: GAS_VOLUME}, "prices": {WATER: PRICE}}
        self.assertFalse(self.season(**water_only)["chauffe"])

    def test_said_it_is_as_the_household_says(self):
        self.assertFalse(self.season(declared=heating.ELECTRICITY)["chauffe"])
        self.assertFalse(self.season(declared=heating.OTHER)["chauffe"])
        water_only = {"readings": [self.readings[1]], "units": {WATER: GAS_VOLUME}, "prices": {WATER: PRICE}}
        said = self.season(declared=heating.GAS, **water_only)
        # The gas is the heating, though nothing tells its part: all of it is shown, not split.
        self.assertEqual((said["chauffe"], said["etat"], said["saison"]["chauffage"]), (True, "peu_lie", None))

    def test_the_electricity_is_read_for_radiators_unless_another_energy_heats(self):
        self.assertTrue(heating.electricity_heats(None))
        self.assertTrue(heating.electricity_heats(heating.ELECTRICITY))
        self.assertFalse(heating.electricity_heats(heating.GAS))
        self.assertFalse(heating.electricity_heats(heating.OTHER))

    def test_no_degree_less_is_advised_on_radiators_the_home_does_not_have(self):
        """« Baissez le chauffage d'un degré » is the radiators' advice: not said once another energy heats the home."""
        from types import SimpleNamespace
        from unittest.mock import patch
        from engine import daily
        said = {"id": "chauffage_degre", "euros_an": 40}
        nothing = lambda *a: None       # noqa: E731
        home = SimpleNamespace(used_days=lambda: {})
        with patch.object(daily, "unusual_day", nothing), patch.object(daily, "contract_option", nothing), \
                patch.object(daily, "baseload", nothing), patch.object(daily, "month_budget", nothing), \
                patch.object(daily, "heating_degree", lambda *a: said):
            self.assertEqual(daily.advices(home, None, {}, NOW, {}, False, None, None, None), [said])
            self.assertEqual(daily.advices(home, None, {}, NOW, {}, False, None, None, None, radiators=False), [])


class GasBill(Invented, unittest.TestCase):
    """The bill's own lines, typed in Réglages (invented figures): 0.09 € a kWh, a subscription of 20 € a month, a CTA
    of 3 €, a TICGN of 15 € a MWh, all before VAT; a cubic metre gives 11 kWh."""
    LINES = gas.Contract(price_kwh=0.09, subscription=20.0, cta=3.0, excise=15.0, before_tax=True, kwh_per_m3=11.0)

    def test_left_empty_the_page_price_is_taken_as_it_is(self):
        empty = gas.Contract()
        self.assertEqual(empty.unit_price(GAS_VOLUME, 1.25), 1.25)
        self.assertEqual(empty.unit_price(GAS_ENERGY, 0.11), 0.11)
        self.assertIsNone(empty.unit_price(GAS_VOLUME, None))        # no price: no euros, never free
        self.assertIsNone(empty.fixed_month())

    def test_the_bill_lines_make_the_price_of_one_unit(self):
        # (0.09 + 0.015) € a kWh, with VAT: 0.126 € ; a cubic metre is 11 of them.
        self.assertAlmostEqual(self.LINES.unit_price(GAS_ENERGY, 0.5), 0.126, places=6)
        self.assertAlmostEqual(self.LINES.unit_price(GAS_VOLUME, 0.5), 0.126 * 11, places=6)
        self.assertAlmostEqual(self.LINES.unit_price(GAS_VOLUME, None), 0.126 * 11, places=6)   # typed: the page's is not needed

    def test_the_excise_alone_is_added_to_the_page_price(self):
        excise = gas.Contract(excise=15.0)
        self.assertAlmostEqual(excise.unit_price(GAS_ENERGY, 0.10), 0.115, places=6)
        # A meter in m³ and no coefficient typed: about 11.2 kWh in a cubic metre.
        self.assertAlmostEqual(excise.unit_price(GAS_VOLUME, 1.25), 1.25 + 0.015 * gas.KWH_PER_M3, places=6)
        self.assertIsNone(excise.unit_price(GAS_VOLUME, None))

    def test_typed_with_taxes_nothing_is_added(self):
        typed = gas.Contract(price_kwh=0.12, subscription=24.0, cta=3.6, kwh_per_m3=11.0)
        self.assertAlmostEqual(typed.unit_price(GAS_VOLUME, 9.9), 1.32, places=6)
        self.assertAlmostEqual(typed.fixed_month(), 27.6, places=6)

    def test_what_is_paid_whatever_is_burnt(self):
        self.assertAlmostEqual(self.LINES.fixed_month(), 23.0 * 1.2, places=6)
        self.assertAlmostEqual(gas.Contract(subscription=20.0).fixed_month(), 20.0, places=6)
        self.assertAlmostEqual(gas.Contract(cta=3.0, before_tax=True).fixed_month(), 3.6, places=6)

    def test_the_month_ends_where_its_pace_leads(self):
        # 25 November, 2 pm: 24 days and 14 hours of a month of 30.
        bill = gas.month_bill(40.0, 27.6, NOW)
        self.assertEqual((bill["gaz"], bill["fixe"]), (40.0, 27.6))
        self.assertAlmostEqual(bill["fin_de_mois"], 40.0 * 30 / (24 + 14 / 24) + 27.6, places=2)
        # The first days of a month say nothing of its end.
        self.assertIsNone(gas.month_bill(3.0, 27.6, datetime(2026, 11, 3, 9, tzinfo=PARIS))["fin_de_mois"])
        # Without a subscription or without a price, no bill: the gas alone is already said.
        self.assertIsNone(gas.month_bill(40.0, None, NOW))
        self.assertIsNone(gas.month_bill(None, 27.6, NOW))

    def test_the_months_of_a_season(self):
        self.assertAlmostEqual(gas.months(date(2026, 10, 1), NOW), 1 + (24 + 14 / 24) / 30, places=6)
        self.assertAlmostEqual(gas.months(date(2026, 10, 1), datetime(2027, 1, 1, tzinfo=PARIS)), 3.0, places=6)

    def test_the_card_gets_the_bill_of_the_month(self):
        fixed = self.LINES.fixed_month()
        price = self.LINES.unit_price(GAS_VOLUME, PRICE)
        season = self.season(prices={HEATING: price, WATER: price}, fixed=fixed)
        bill = season["facture"]
        self.assertAlmostEqual(season["prix"], 0.126 * 11, places=4)
        self.assertEqual(bill["gaz"], season["mois"]["eur"])
        self.assertAlmostEqual(bill["fixe"], 27.6, places=2)
        self.assertAlmostEqual(bill["fin_de_mois"], season["mois"]["eur"] * 30 / (24 + 14 / 24) + 27.6, delta=0.02)
        # Since 1 October: October whole and November so far.
        self.assertAlmostEqual(season["saison"]["abonnement"], 27.6 * (1 + (24 + 14 / 24) / 30), delta=0.01)

    def test_without_a_subscription_no_bill_is_said(self):
        season = self.season()
        self.assertIsNone(season["facture"])
        self.assertIsNone(season["saison"]["abonnement"])
        self.assertIsNone(self.season(prices={HEATING: PRICE}, fixed=27.6)["facture"])     # a meter without a price: no euros


class GasUnit(unittest.TestCase):
    def test_the_unit_class_says_it(self):
        self.assertEqual(gas_unit({"unit_class": "energy", "unit_of_measurement": "kWh"}), "kWh")
        self.assertEqual(gas_unit({"unit_class": "volume", "unit_of_measurement": "m³"}), "m³")
        self.assertEqual(gas_unit({"unit_class": "volume", "statistics_unit_of_measurement": "ft³"}), "m³")

    def test_else_the_unit(self):
        self.assertEqual(gas_unit({"unit_of_measurement": "Wh"}), "kWh")
        self.assertEqual(gas_unit({"unit_class": None, "statistics_unit_of_measurement": "m³"}), "m³")

    def test_neither_is_not_guessed(self):
        self.assertIsNone(gas_unit(None))
        self.assertIsNone(gas_unit({"unit_class": "mass", "unit_of_measurement": "kg"}))
        self.assertIsNone(gas_unit({"unit_of_measurement": "impulsions"}))


if __name__ == "__main__":
    unittest.main()


try:
    import sys
    from types import SimpleNamespace
    from unittest.mock import patch

    sys.path.insert(0, str(ROOT))
    from custom_components.hestia_energy import coordinator as coordinator_module, hub_view, reader, websocket  # noqa: E402
    from custom_components.hestia_energy.engine import sources  # noqa: E402
except ImportError:          # Home Assistant absent: tested on GitHub
    hub_view = None

STOVE = "sensor.poele_granules_energie"
CUISINE = "sensor.gaz_cuisine"


@unittest.skipIf(hub_view is None, "Home Assistant absent")
class InTheBrick(unittest.TestCase):
    """The same invented home in the coordinator and in the panel's pages (their own state only, the brick not started)."""

    @classmethod
    def setUpClass(cls):
        GasHome.setUpClass()
        cls.cold, cls.readings = GasHome.cold, GasHome.readings

    def coordinator(self, **settings):
        c = coordinator_module.EnergyCoordinator.__new__(coordinator_module.EnergyCoordinator)
        c.tz, c.cold, c.settings = PARIS, self.cold, {**coordinator_module.DEFAULTS, **settings}
        c.gas_units = {HEATING: GAS_VOLUME, WATER: GAS_VOLUME, STOVE: GAS_ENERGY}
        c.gas_prices = {HEATING: PRICE, WATER: PRICE}
        c.extras = {}
        return c

    def home(self, *more):
        return SimpleNamespace(of=lambda kind: [*self.readings, *more] if kind == "gas" else [])

    def test_the_gas_joins_the_heating(self):
        gas = self.coordinator()._gas(self.home(), NOW, "oui")
        self.assertEqual((gas["etat"], gas["unite"]), ("pret", "m³"))
        self.assertEqual(self.coordinator()._gas(self.home(), NOW, "non")["etat"], "sans_meteo")
        self.assertIsNone(self.coordinator()._gas(SimpleNamespace(of=lambda kind: []), NOW, "oui"))

    def test_a_stove_declared_as_gas_is_not_gas(self):
        """The pellet stove on the page as « gas », in kWh (D6): it stays the stove's, the boiler's m³ are counted alone.
        Once the household says it does burn gas, the two units cannot be added up, and nothing is said."""
        stove = reading(STOVE, "Poêle à granulés", lambda d: 5.0)
        self.assertEqual(self.coordinator()._gas(self.home(stove), NOW, "oui")["unite"], "m³")
        self.assertIsNone(self.coordinator(stove_fuel="gas")._gas(self.home(stove), NOW, "oui"))

    def test_each_meters_price_is_read_from_the_page(self):
        c = self.coordinator()
        c.page = sources.EnergyPage(sources.FORMAT_2026, gas=[
            Meter("gas", HEATING, "Chauffage", Price(entity="sensor.gaz_prix_m3")), Meter("gas", WATER, "Eau chaude", Price(number=1.3)),
            Meter("gas", "sensor.gaz_cuisine", "Cuisine", Price(entity="sensor.absent"))])
        c.hass = SimpleNamespace(states=SimpleNamespace(get={"sensor.gaz_prix_m3": SimpleNamespace(state="1.31")}.get))
        self.assertEqual(c._gas_prices(), {HEATING: 1.31, WATER: 1.3})

    def test_the_bill_lines_typed_in_settings_make_each_meters_price(self):
        """The price typed replaces the page's (a meter without one gets it too), the TICGN and VAT are added; a meter
        whose unit is not known keeps the page's price, and is not counted anyway."""
        c = self.coordinator(gas_price=0.09, gas_ticgn=15.0, gas_ht=True, gas_kwh_m3=11.0)
        c.gas_units[CUISINE] = GAS_ENERGY
        c.page = sources.EnergyPage(sources.FORMAT_2026, gas=[
            Meter("gas", HEATING, "Chauffage", Price(entity="sensor.gaz_prix_m3")), Meter("gas", WATER, "Eau chaude", Price(number=1.3)),
            Meter("gas", CUISINE, "Cuisine", Price(entity="sensor.absent")), Meter("gas", "sensor.inconnu", "?", Price(number=2.0))])
        c.hass = SimpleNamespace(states=SimpleNamespace(get={"sensor.gaz_prix_m3": SimpleNamespace(state="1.31")}.get))
        prices = c._gas_prices()
        self.assertAlmostEqual(prices[HEATING], 0.126 * 11, places=6)
        self.assertAlmostEqual(prices[WATER], 0.126 * 11, places=6)
        self.assertAlmostEqual(prices[CUISINE], 0.126, places=6)
        self.assertEqual(prices["sensor.inconnu"], 2.0)
        # Only the TICGN typed: it is added to the page's price, and a meter without a price stays without.
        c.settings.update(gas_price=None, gas_ht=False)
        prices = c._gas_prices()
        self.assertAlmostEqual(prices[HEATING], 1.31 + 0.015 * 11, places=6)
        self.assertNotIn(CUISINE, prices)

    def test_the_subscription_typed_gives_the_month_bill(self):
        gas_ = self.coordinator(gas_subscription=20.0, gas_cta=3.0, gas_ht=True)._gas(self.home(), NOW, "oui")
        self.assertAlmostEqual(gas_["facture"]["fixe"], 27.6, places=2)
        self.assertGreater(gas_["facture"]["fin_de_mois"], gas_["mois"]["eur"] + 27.6)
        self.assertIsNone(self.coordinator()._gas(self.home(), NOW, "oui")["facture"])

    def test_what_heats_the_home_said_in_settings(self):
        """Gas said: no radiators are read in the electricity, whatever the weather extension's state; electricity
        said: the gas is counted, not shown as heating."""
        for said in ("gas", "other"):
            heat = self.coordinator(heating=said)._heating(self.home(), NOW, None, "non")
            self.assertEqual(heat, {"etat": "autre_energie", "source": said, "poele": None})
        self.assertTrue(self.coordinator(heating="gas")._gas(self.home(), NOW, "oui")["chauffe"])
        self.assertFalse(self.coordinator(heating="electricity")._gas(self.home(), NOW, "oui")["chauffe"])
        self.assertEqual(self.coordinator(heating="electricity")._heating(self.home(), NOW, None, "non")["etat"], "sans_meteo")

    def test_the_settings_accept_the_bill_lines(self):
        lines = {"heating": "gas", "gas_price": 0.09, "gas_subscription": 20, "gas_cta": 3, "gas_ticgn": 15, "gas_ht": True,
                 "gas_kwh_m3": 11}
        self.assertEqual(websocket.SETTINGS(lines)["gas_subscription"], 20.0)
        self.assertEqual(websocket.SETTINGS({k: None for k in lines if k != "gas_ht"})["heating"], None)
        for wrong in ({"heating": "bois"}, {"gas_ticgn": -1}, {"gas_kwh_m3": 110}, {"gas_ht": "oui"}, {"gas_price": 50}):
            with self.assertRaises(Exception, msg=wrong):
                websocket.SETTINGS(wrong)
        self.assertTrue(set(lines) <= set(websocket.KEYS))
        self.assertTrue(set(lines) <= set(coordinator_module.DEFAULTS))
        # An automation may follow the gas prices, not say what heats the home.
        self.assertEqual(websocket.SERVICE_SCHEMA({"gas_price": 0.1, "gas_ticgn": 16})["gas_ticgn"], 16.0)
        with self.assertRaises(Exception):
            websocket.SERVICE_SCHEMA({"heating": "gas"})

    def test_the_panel_says_the_bill_and_the_household_s_word(self):
        gas_ = self.coordinator(gas_subscription=27.6)._gas(self.home(), NOW, "oui")
        page = sources.EnergyPage(sources.FORMAT_2026, imports=[Meter("import", "sensor.linky")],
                                  gas=[r.meter for r in self.readings])
        c = SimpleNamespace(data={"chauffage": {"etat": "autre_energie", "source": "gas", "poele": None, "gaz": gas_}}, page=page, rows={},
                            reference={}, settings={**coordinator_module.DEFAULTS, "heating": "gas"}, extras={}, contract=None,
                            level=sources.Level(0, True, False, False, False, True))
        hass = SimpleNamespace(states=SimpleNamespace(get=lambda entity_id: None))
        with patch.object(reader, "origins", lambda hass, stats: {}), patch.object(hub_view, "todos", lambda hass, c: []):
            source = next(s for s in hub_view.build_sources(hass, c) if s["id"] == "gaz")
        self.assertEqual(len(source["chiffres"]), 3)
        self.assertRegex(source["chiffres"][2]["texte"], r"^\d+ € ce mois, abonnement compris$")
        line = next(a for a in hub_view._abilities(hass, c, []) if a["id"] == "chauffage")
        self.assertEqual((line["etat"], line["avec"]), ("ok", "avec Hestia Weather"))
        # Another energy said, or the gas said not to heat: the cold's line is not the heating's.
        c.data["chauffage"] = {"etat": "autre_energie", "source": "other", "poele": None, "gaz": {**gas_, "chauffe": False}}
        line = next(a for a in hub_view._abilities(hass, c, []) if a["id"] == "chauffage")
        self.assertEqual((line["etat"], line["avec"]), ("non", "la maison se chauffe autrement, d’après vos réglages"))

    def test_settings_show_what_was_found_and_what_is_counted(self):
        """Réglages: what the cold shows heats the home, the page's price of a cubic metre, and what Hestia counts once
        the bill's lines are typed."""
        c = self.coordinator(gas_subscription=20.0, gas_cta=3.0, gas_ticgn=15.0, gas_ht=True, gas_kwh_m3=11.0)
        c.page = sources.EnergyPage(sources.FORMAT_2026, imports=[Meter("import", "sensor.linky")], gas=[r.meter for r in self.readings])
        c.table, c.page_prices, c.found_extras, c.offpeak_found = {}, {}, {}, None
        c.hass = SimpleNamespace(states=SimpleNamespace(get={"sensor.gaz_prix_m3": SimpleNamespace(state="1.25")}.get),
                                 services=SimpleNamespace(async_services=lambda: {}), config=SimpleNamespace(components=set()))
        c.gas_prices = c._gas_prices()
        c.data = {"chauffage": {"etat": "peu_lie", "poele": None, "gaz": c._gas(self.home(), NOW, "oui")}}
        found = hub_view.found_settings(c.hass, c)
        self.assertEqual(found["heating"], {"valeur": "gas", "source": "trouvé d’après le froid"})
        self.assertTrue(found["a"]["gaz"])
        self.assertEqual((found["gaz"]["unite"], found["gaz"]["prix_page"], found["gaz"]["kwh_m3"]), ("m³", 1.25, 11.2))
        self.assertAlmostEqual(found["gaz"]["prix"], (1.25 + 0.015 * 11) * 1.2, places=4)
        self.assertAlmostEqual(found["gaz"]["fixe"], 27.6, places=6)
        # A home without gas: nothing found, no gas section.
        c.page = sources.EnergyPage(sources.FORMAT_2026, imports=[Meter("import", "sensor.linky")])
        c.data = {"chauffage": {"etat": "pret", "poele": None, "gaz": None}}
        found = hub_view.found_settings(c.hass, c)
        self.assertEqual((found["heating"]["valeur"], found["a"]["gaz"], found["gaz"]["unite"]), ("electricity", False, None))

    def test_the_panel_says_the_gas_of_the_season_and_the_heating_from_the_cold(self):
        gas = self.coordinator()._gas(self.home(), NOW, "oui")
        page = sources.EnergyPage(sources.FORMAT_2026, imports=[Meter("import", "sensor.linky")],
                                  gas=[r.meter for r in self.readings])
        c = SimpleNamespace(data={"chauffage": {"etat": "peu_lie", "poele": None, "gaz": gas}}, page=page, rows={}, reference={},
                            settings=dict(coordinator_module.DEFAULTS), extras={}, contract=None,
                            level=sources.Level(0, True, False, False, False, True))
        hass = SimpleNamespace(states=SimpleNamespace(get=lambda entity_id: None))
        with patch.object(reader, "origins", lambda hass, stats: {}), patch.object(hub_view, "todos", lambda hass, c: []):
            source = next(s for s in hub_view.build_sources(hass, c) if s["id"] == "gaz")
        self.assertEqual([x["texte"] for x in source["chiffres"]], ["110 m³ cette saison", "138 €"])
        heating_line = next(a for a in hub_view._abilities(hass, c, []) if a["id"] == "chauffage")
        self.assertEqual((heating_line["etat"], heating_line["avec"]), ("ok", "avec Hestia Weather"))
        # Still learning: the gas's days are said, not « la maison se chauffe surtout autrement ».
        c.data["chauffage"]["gaz"] = {**gas, "etat": "apprend", "jours": 24}
        heating_line = next(a for a in hub_view._abilities(hass, c, []) if a["id"] == "chauffage")
        self.assertEqual((heating_line["etat"], heating_line["avec"]), ("attend", "en apprentissage : 24 jours sur 60"))
        # Gas for the hot water only: nothing changes for a home heated otherwise.
        c.data["chauffage"]["gaz"] = {**gas, "etat": "peu_lie"}
        self.assertEqual(next(a for a in hub_view._abilities(hass, c, []) if a["id"] == "chauffage")["etat"], "non")
