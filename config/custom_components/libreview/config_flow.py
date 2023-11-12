"""Config flow for LibreView integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv

from . import librepy


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LibreView."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._data = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        user_input = user_input or {}

        schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=1): cv.positive_int,
            }
        )

        if not user_input:
            return self.async_show_form(step_id="user", data_schema=schema)

        if not (errors := await validate_input(self.hass, user_input)):
            return self.async_create_entry(
                title=user_input[CONF_EMAIL], data=user_input
            )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


async def validate_input(
    hass: core.HomeAssistant, data: dict[str, str]
) -> dict[str, str]:
    """Validate the user input allows us to connect."""

    is_connected = await librepy.connect(CONF_EMAIL, CONF_PASSWORD)

    if not is_connected[0]:
        return {"base": is_connected[1]}

    return {}
