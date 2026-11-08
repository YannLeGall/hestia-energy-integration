"""The websocket commands of the card and the tab (INTERFACE.md § 1.3). Read only, quick: everything is in the
coordinator already (socle rule: under 0.25 s a command); `periods` computes in a worker thread."""
from __future__ import annotations

from datetime import date

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import callback

from .const import DOMAIN
from .engine import report

RUBRIQUES = ("soleil", "chauffage", "eau", "contrat", "appareils", "veille", "pointe")


def _coordinator(hass):
    entry = next((e for e in hass.config_entries.async_entries(DOMAIN) if getattr(e, "runtime_data", None)), None)
    return entry.runtime_data if entry else None


def async_setup_websocket(hass) -> None:
    for command in (ws_view, ws_detail, ws_periods, ws_sources, ws_simulate, ws_settings, ws_set_settings):
        websocket_api.async_register_command(hass, command)


@websocket_api.websocket_command({vol.Required("type"): "hestia_energy/view"})
@callback
def ws_view(hass, connection, msg):
    """Everything the full card shows: the banner, « Maintenant », the reports, the level."""
    c = _coordinator(hass)
    if c is None:
        connection.send_error(msg["id"], "not_ready", "Hestia Énergie n'est pas activée.")
        return
    connection.send_result(msg["id"], {"version": 1, **c.data})


@websocket_api.websocket_command({vol.Required("type"): "hestia_energy/detail", vol.Required("rubrique"): vol.In(RUBRIQUES)})
@callback
def ws_detail(hass, connection, msg):
    """One detail card. What is not built yet says so (« bientot »), never an empty card that looks finished."""
    c = _coordinator(hass)
    if c is None:
        connection.send_error(msg["id"], "not_ready", "Hestia Énergie n'est pas activée.")
        return
    d, live = c.data, c.data.get("direct") or {}
    rubrique = msg["rubrique"]
    if rubrique == "veille":
        out = {"veille": d.get("veille"), "hausse": d.get("veille_hausse")}
    elif rubrique == "contrat":
        out = {"contrat": d.get("contrat"), "heures_creuses": d.get("heures_creuses"), "prix": live.get("prix"),
               "periode": live.get("periode"), "prochain_changement": live.get("prochain_changement"), "simulateur": "bientot"}
    elif rubrique == "pointe":
        out = {"achat_w": live.get("achat_w"), "kva": (d.get("contrat") or {}).get("kva"), "en_marche": live.get("en_marche")}
    elif rubrique == "soleil":
        out = {"jour": d.get("jour"), "hier": d.get("hier"), "soleil_w": live.get("soleil_w"), "revente_w": live.get("revente_w"),
               "sources": (live.get("sources") or {}).get("soleil"), "voies": "bientot"}
    elif rubrique == "eau":
        out = {"fuite": live.get("fuite"), "jour": "bientot"}
    elif rubrique == "appareils":
        out = {"en_marche": live.get("en_marche"), "repartition": "bientot"}
    else:
        out = {"chauffage": d.get("chauffage")}
    connection.send_result(msg["id"], {"rubrique": rubrique, **out})


@websocket_api.websocket_command({vol.Required("type"): "hestia_energy/periods", vol.Required("du"): str, vol.Required("au"): str,
                                  vol.Required("pas"): vol.In(("jour", "semaine", "mois", "annee"))})
@websocket_api.async_response
async def ws_periods(hass, connection, msg):
    c = _coordinator(hass)
    if c is None or c.home is None or c.contract is None:
        connection.send_error(msg["id"], "not_ready", "Les bilans ne sont pas encore prêts.")
        return
    try:
        start, end = date.fromisoformat(msg["du"]), date.fromisoformat(msg["au"])
    except ValueError:
        connection.send_error(msg["id"], "invalid", "Dates attendues au format AAAA-MM-JJ.")
        return
    if end < start or (end - start).days > 800:
        connection.send_error(msg["id"], "invalid", "Une période de deux ans au plus.")
        return
    rows = await hass.async_add_executor_job(report.periods, c.home, c.contract, c.table, start, end, msg["pas"])
    connection.send_result(msg["id"], {"pas": msg["pas"], "periodes": [p.as_dict() for p in rows]})


@websocket_api.websocket_command({vol.Required("type"): "hestia_energy/sources"})
@callback
def ws_sources(hass, connection, msg):
    """The arbiter: each live quantity, its source and those set aside; the findings on the statistics."""
    c = _coordinator(hass)
    if c is None:
        connection.send_error(msg["id"], "not_ready", "Hestia Énergie n'est pas activée.")
        return
    page = c.page
    meters = [] if page is None else [{"type": m.kind, "stat": m.stat, "nom": m.name, "periode": m.period,
                                        "puissance": list(m.power.entities)} for m in page.meters]
    connection.send_result(msg["id"], {"direct": (c.data.get("direct") or {}).get("sources"), "constats": c.data.get("constats"),
                                       "compteurs": meters, "format_page": None if page is None else page.format,
                                       "extensions": c.data.get("extensions"), "equipement": c.data.get("equipement")})


@websocket_api.websocket_command({vol.Required("type"): "hestia_energy/simulate"})
@callback
def ws_simulate(hass, connection, msg):
    """The contract simulator (F3) comes with the first stable version."""
    connection.send_error(msg["id"], "not_supported", "Le simulateur de contrat arrive avec la première version stable.")


SETTINGS = vol.Schema({
    vol.Optional("kva"): vol.Any(None, vol.All(int, vol.In((3, 6, 9, 12, 15, 18, 24, 30, 36)))),
    vol.Optional("margin"): vol.All(vol.Coerce(float), vol.Range(min=0, max=0.3)),
    vol.Optional("export_price"): vol.Any(None, vol.All(vol.Coerce(float), vol.Range(min=0, max=1))),
    vol.Optional("option"): vol.Any(None, vol.In(("base", "hphc", "tempo"))),
    vol.Optional("notify_service"): vol.Any(None, vol.All(str, vol.Match(r"^notify\.[a-z0-9_]+$"))),
    vol.Optional("notify_hour"): vol.All(vol.Coerce(int), vol.Range(min=0, max=23)),
    vol.Optional("offpeak"): vol.Any(None, vol.All(str, vol.Length(max=60))),
    vol.Optional("bag_price"): vol.Any(None, vol.All(vol.Coerce(float), vol.Range(min=0, max=100))),
})


@websocket_api.websocket_command({vol.Required("type"): "hestia_energy/settings"})
@websocket_api.require_admin
@callback
def ws_settings(hass, connection, msg):
    """The household's settings with what Hestia found by itself (the value used when a setting is left empty)."""
    c = _coordinator(hass)
    if c is None:
        connection.send_error(msg["id"], "not_ready", "Hestia Énergie n'est pas activée.")
        return
    found = {"kva": (c.extras or {}).get("kva"), "option": (c.data.get("contrat") or {}).get("option"),
             "export_price": c.contract.export_price if c.contract else None,
             "poele": bool((c.extras or {}).get("pellets")),
             "heures_creuses": None if c.offpeak is None or c.offpeak.source == "réglage" else
             " et ".join(f"de {a} à {b}" for a, b in (r.label() for r in c.offpeak.ranges))}
    connection.send_result(msg["id"], {"reglages": {k: c.settings.get(k) for k in ("kva", "margin", "export_price", "option", "bag_price",
                                                                                 "notify_service", "notify_hour", "offpeak")},
                                       "trouve": found})


@websocket_api.websocket_command({vol.Required("type"): "hestia_energy/set_settings", vol.Required("reglages"): dict})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_set_settings(hass, connection, msg):
    c = _coordinator(hass)
    if c is None:
        connection.send_error(msg["id"], "not_ready", "Hestia Énergie n'est pas activée.")
        return
    try:
        changes = SETTINGS(msg["reglages"])
    except vol.Invalid as err:
        connection.send_error(msg["id"], "invalid", str(err))
        return
    await c.async_save_settings(changes)
    connection.send_result(msg["id"], {"enregistre": True})
