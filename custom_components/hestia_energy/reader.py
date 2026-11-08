"""What Hestia Energy reads in Home Assistant, and nothing else: the Energy page, the long-term statistics, the states.

Read only (principle 1): no statistic, entity or setting of Home Assistant is ever written here. Every Recorder read
runs in the Recorder's own thread; a Recorder that cannot answer gives empty rows, never an exception to the caller.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
import re

from homeassistant.components.recorder import get_instance, statistics
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.loader import async_get_integration, async_get_loaded_integration

_LOGGER = logging.getLogger(__name__)
# Units the statistics are read in, whatever the sensor's own (a meter in Wh comes in kWh).
UNITS = {"energy": "kWh", "power": "W", "volume": "L", "volume_flow_rate": "L/min", "mass": "kg"}


async def energy_prefs(hass: HomeAssistant) -> dict | None:
    """The Energy page as `energy/get_prefs` gives it, or None when it was never filled."""
    try:
        from homeassistant.components.energy.data import async_get_manager
        manager = await async_get_manager(hass)
    except Exception as err:  # noqa: BLE001 - no Energy page: the brick says what to do, it does not stop
        _LOGGER.debug("Energy page unavailable: %s", err)
        return None
    return dict(manager.data) if manager.data else None


async def listen_prefs(hass: HomeAssistant, callback) -> None:
    """Call `callback` (a coroutine function) when the Energy page changes."""
    try:
        from homeassistant.components.energy.data import async_get_manager
        manager = await async_get_manager(hass)
        manager.async_listen_updates(callback)
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Energy page not followed: %s", err)


async def metadata(hass: HomeAssistant, ids: set[str]) -> dict[str, dict]:
    if not ids:
        return {}
    try:
        found = await get_instance(hass).async_add_executor_job(lambda: statistics.get_metadata(hass, statistic_ids=ids))
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Statistics metadata unavailable: %s", err)
        return {}
    return {sid: dict(meta) for sid, (_, meta) in found.items()}


async def hourly(hass: HomeAssistant, ids: set[str], start: datetime, end: datetime | None = None) -> dict[str, list[dict]]:
    """Each statistic's hours since `start`: {id: [{start (aware, UTC), mean, min, max, sum}]}, in kWh, W, L."""
    if not ids:
        return {}

    def read():
        rows = statistics.statistics_during_period(hass, start, end, ids, "hour", UNITS, {"mean", "min", "max", "sum"})
        return {sid: [{"start": _when(r["start"]), "mean": r.get("mean"), "min": r.get("min"), "max": r.get("max"),
                       "sum": r.get("sum")} for r in values] for sid, values in rows.items()}

    try:
        return await get_instance(hass).async_add_executor_job(read)
    except Exception as err:  # noqa: BLE001 - no statistics: the reports say so, nothing is invented
        _LOGGER.warning("Statistics unavailable: %s", err)
        return {}


def _when(value) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(UTC)
    return datetime.fromtimestamp(value, UTC)


# --- What the home has besides the Energy page (extensions, F1, 8.3) --------------------------------------------

_PERIOD_STATE = re.compile(r"^(heures? (pleines?|creuses?)|h[pc](\b|\.\.))", re.I)
_TEMPO = re.compile(r"tempo", re.I)
_COLOURS = {"bleu": "bleu", "blue": "bleu", "blanc": "blanc", "white": "blanc", "rouge": "rouge", "red": "rouge"}
_KVA = re.compile(r"(\d{1,2}) ?kva", re.I)


def period_of(state: str | None) -> str | None:
    """« HEURE PLEINE », « HC.. », « heures creuses » → « hp » / « hc »."""
    text = (state or "").strip().lower()
    if "creuse" in text or text.startswith("hc"):
        return "hc"
    if "pleine" in text or text.startswith("hp"):
        return "hp"
    return None


def colour_of(state: str | None) -> str | None:
    return _COLOURS.get((state or "").strip().lower())


def detect(hass: HomeAssistant) -> dict:
    """What can be read beyond the page: the meter's period (TIC), the Tempo colours, the inverters' channels,
    the subscribed power written in an entity's name (« option_hphc_9kva »). Each found entity id, or None."""
    registry = er.async_get(hass)
    found = {"period": None, "tempo_today": None, "tempo_tomorrow": None, "inverter": None, "channels": [], "kva": None,
             "comwatt": False}
    for state in hass.states.async_all("sensor"):
        eid = state.entity_id
        if found["period"] is None and _PERIOD_STATE.match(state.state or "") and not _TEMPO.search(eid):
            found["period"] = eid
        if _TEMPO.search(eid) and colour_of(state.state):
            key = "tempo_tomorrow" if re.search(r"demain|tomorrow|prochain|next", eid) else "tempo_today"
            found[key] = found[key] or eid
    for entry in registry.entities.values():
        if entry.platform == "opendtu" and entry.domain == "sensor":
            if re.search(r"_ch\d+_power$", entry.entity_id):
                found["channels"].append(entry.entity_id)
            elif entry.entity_id.endswith("_ac_power"):
                found["inverter"] = found["inverter"] or entry.entity_id
        if entry.platform == "comwatt":
            found["comwatt"] = True
        if found["kva"] is None and (match := _KVA.search(entry.entity_id)):
            found["kva"] = int(match.group(1))
    if not found["inverter"]:
        # OpenDTU seen by its names only (a copy by Remote Home-Assistant, or entities without their registry entry).
        names = [s.entity_id for s in hass.states.async_all("sensor")]
        found["inverter"] = next((n for n in names if re.match(r"sensor\.opendtu_\w+_ac_power$", n)), None)
        if found["inverter"] and not found["channels"]:
            found["channels"] = [n for n in names if re.search(r"_ch\d+_power$", n)]
    found["channels"].sort()
    found["pellets"] = pellet_tracking(hass)
    return found


def pellet_tracking(hass: HomeAssistant) -> dict | None:
    """Suivi Stock Pellet (the pellet stove's extension): its sensors found by the role each one carries
    (`suivi_stock_pellet_key`), so a renamed entity, or a copy of it, is still found; the season's purchases and the
    bag's weight. None without it."""
    roles = {}
    for state in hass.states.async_all("sensor"):
        key = state.attributes.get("suivi_stock_pellet_key")
        if key and key not in roles:
            roles[key] = state
    if "consomme_kg" not in roles:
        return None

    def number(role):
        try:
            return float(roles[role].state) if role in roles else None
        except (TypeError, ValueError):
            return None

    stock = roles.get("stock")
    return {"consumed": roles["consomme_kg"].entity_id, "season_kg": number("consomme_kg"), "spent_eur": number("depense"), "bought_kg": number("achete_kg"),
            "bag_kg": stock.attributes.get("poids_sac_kg") if stock else None}


def origins(hass: HomeAssistant, stats: list[str]) -> dict[str, dict]:
    """Where each statistic comes from: its integration and its device's maker and model (« Comwatt », « LiXee
    ZLinky »). An imported statistic (« linky:… ») has neither; its prefix says it."""
    entities, devices = er.async_get(hass), dr.async_get(hass)
    out = {}
    for stat in stats:
        entry = entities.async_get(stat) if "." in stat and ":" not in stat else None
        device = devices.async_get(entry.device_id) if entry and entry.device_id else None
        out[stat] = {"platform": entry.platform if entry else None,
                     "maker": device.manufacturer if device else None,
                     "integration": _integration_name(hass, entry.platform) if entry else None,
                     "device": " ".join(x for x in (device.manufacturer, device.model) if x) if device else None}
    return out


def _integration_name(hass: HomeAssistant, domain: str) -> str | None:
    """The integration's own name (« Remote Home-Assistant »), never its technical domain; None for a template."""
    if domain in ("template", "utility_meter", "integration", "statistics", "sql"):
        return None
    try:
        return async_get_loaded_integration(hass, domain).name
    except Exception:  # noqa: BLE001
        return None


async def is_local(hass: HomeAssistant, entity_id: str) -> bool | None:
    """True when the entity's integration works locally (its `iot_class`), None when unknown (a template)."""
    entry = er.async_get(hass).async_get(entity_id)
    if entry is None or entry.platform in ("template", "utility_meter", "integration", "statistics", "sql"):
        return None
    try:
        integration = await async_get_integration(hass, entry.platform)
    except Exception:  # noqa: BLE001
        return None
    iot = integration.iot_class or ""
    return iot.startswith("local") if iot else None


# --- What the other Hestia bricks give (their public interfaces, never their insides) ----------------------------

WEATHER_API = "hestia_weather_api"


def weather_cold(hass: HomeAssistant) -> str:
    """Can Hestia Weather give the degree-days? « oui », « ancienne » (installed, too old for `degree_days`), « non »."""
    api = hass.data.get(WEATHER_API)
    if api is None:
        return "non"
    return "oui" if hasattr(api, "degree_days") else "ancienne"


async def degree_days(hass: HomeAssistant, days: list) -> dict:
    """Each day's heating degree-days from Hestia Weather ({date: DJU}); a day it cannot give is left out."""
    api = hass.data.get(WEATHER_API)
    out = {}
    if api is None or not hasattr(api, "degree_days"):
        return out
    for day in days:
        try:
            found = await api.degree_days(day)
        except Exception as err:  # noqa: BLE001 - another brick's trouble never stops this one
            _LOGGER.debug("Degree-days of %s unavailable: %s", day, err)
            continue
        if found and found.get("heating") is not None:
            out[day] = float(found["heating"])
    return out


_STOVE_NAME = re.compile(r"po[eê]le|pellet|granul|bois|wood|stove|insert", re.I)


def thermostats(hass: HomeAssistant) -> list:
    """The home's thermostats as Hestia Energy needs them (9.5): heating or not, and the power drawn when heating —
    Versatile Thermostat's own figure (the heater's power × its share of the cycle). A thermostat of a stove (by its
    name) heats without electricity to count. Vents and copies without a room temperature are left out."""
    from .engine.heating import Thermostat
    out = []
    for state in hass.states.async_all("climate"):
        a = state.attributes
        if state.state in ("unavailable", "unknown") or a.get("current_temperature") is None:
            continue
        name = a.get("friendly_name") or state.entity_id
        power = (a.get("power_manager") or {}) if isinstance(a.get("power_manager"), dict) else {}
        watts = power.get("mean_cycle_power")
        if watts is None and power.get("device_power") is not None and a.get("on_percent") is not None:
            watts = power["device_power"] * a["on_percent"]
        try:
            watts = None if watts is None else float(watts)
        except (TypeError, ValueError):
            watts = None
        out.append(Thermostat(name=name, heating=a.get("hvac_action") == "heating", watts=watts,
                              stove=bool(_STOVE_NAME.search(f"{state.entity_id} {name}"))))
    return out


async def colour_history(hass: HomeAssistant, entity_id: str, start: datetime) -> dict:
    """The Tempo colour of each day the Recorder still keeps for `entity_id` ({date: « bleu »…}), read at the day's
    noon (a Tempo day runs from 6 h to 6 h). The Recorder keeps about ten days; the brick keeps them afterwards."""
    from homeassistant.components.recorder import history
    from homeassistant.util import dt as dt_util

    def read():
        return history.state_changes_during_period(hass, start, None, entity_id, include_start_time_state=True)

    try:
        found = await get_instance(hass).async_add_executor_job(read)
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Tempo history unavailable: %s", err)
        return {}
    states = found.get(entity_id, [])
    return colours_by_day([(dt_util.as_local(x.last_changed), x.state) for x in states], dt_util.now())


def colours_by_day(changes: list, now: datetime) -> dict:
    """Each Tempo day whose noon falls while a colour was shown ({date: colour}); a colour kept for days counts for
    each of them. `changes`: (local time, state) in order."""
    out = {}
    for (since, state), following in zip(changes, [*[c[0] for c in changes[1:]], now]):
        colour = colour_of(state)
        if not colour:
            continue
        day = (since - timedelta(hours=6)).date()
        while True:
            noon = since.replace(year=day.year, month=day.month, day=day.day, hour=12, minute=0, second=0, microsecond=0)
            if noon >= following:
                break
            if noon >= since:
                out[day] = colour
            day += timedelta(days=1)
    return out


async def reference_statistics(hass: HomeAssistant) -> dict:
    """The bill's own meter (Enedis) when HA Linky or MyElectricalData imports it, even outside the Energy page:
    {« achats »: statistic id, « revente »: statistic id}; empty without it."""
    def read():
        return statistics.list_statistic_ids(hass)

    try:
        found = await get_instance(hass).async_add_executor_job(read)
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Statistics list unavailable: %s", err)
        return {}
    out = {}
    for item in found:
        sid, source = item.get("statistic_id", ""), (item.get("source") or "").lower()
        head = sid.split(":", 1)[0].lower() if ":" in sid else ""
        if head == "linky" or source == "linky":
            out.setdefault("achats", sid)
        elif head == "linky_prod" or source == "linky_prod":
            out.setdefault("revente", sid)
        elif "myelectricaldata" in head or "myelectricaldata" in source:
            out.setdefault("revente" if "production" in sid.lower() else "achats", sid)
    return out
