"""One home, one entry: everything else is set in the « Énergie » tab of the Hestia-FB panel."""
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.core import callback

from . import reader
from .const import DOMAIN, HOME_UNIQUE_ID
from .engine import sources


class EnergyConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(HOME_UNIQUE_ID)
        self._abort_if_unique_id_configured()
        # D21: a consumption source in the Energy page is the one thing required; without it the brick has nothing
        # to read, so it is not installed and the shortest paths are shown instead (checked again on each try).
        if sources.read_page(await reader.energy_prefs(self.hass)).empty:
            return self.async_show_form(step_id="user", data_schema=vol.Schema({}), errors={"base": "no_source"},
                                        description_placeholders=_paths(), last_step=True)
        if user_input is not None:
            return self.async_create_entry(title="Ma maison", data={})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}), last_step=True,
                                    description_placeholders=_paths())

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return EnergyOptionsFlow()


def _paths() -> dict:
    links = {s["type"]: s["lien"] for s in sources.OFFICIAL}
    return {"ha_linky": links[sources.HA_LINKY], "myelectricaldata": links[sources.MYELECTRICALDATA],
            "tic": links[sources.TIC], "energy": "/config/energy"}


class EnergyOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=dict(self.config_entry.options))
        return self.async_show_form(step_id="init", data_schema=vol.Schema({}),
            description_placeholders={"link": "/hestia/energie"})
