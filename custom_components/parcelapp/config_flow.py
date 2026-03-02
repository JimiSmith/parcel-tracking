"""Config flow for ParcelApp."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ParcelAppApiAuthError, ParcelAppApiClient, ParcelAppApiError
from .const import (
    CONF_API_KEY,
    CONF_FILTER_MODE,
    CONF_SCAN_INTERVAL,
    DEFAULT_FILTER_MODE,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DOMAIN,
    FILTER_MODES,
    MIN_SCAN_INTERVAL_SECONDS,
    TITLE,
)


class ParcelAppConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ParcelApp."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            mode = user_input[CONF_FILTER_MODE]

            try:
                await ParcelAppApiClient(
                    async_get_clientsession(self.hass), api_key
                ).async_get_deliveries(mode)
            except ParcelAppApiAuthError:
                errors["base"] = "invalid_auth"
            except ParcelAppApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=TITLE,
                    data={
                        CONF_API_KEY: api_key,
                        CONF_FILTER_MODE: mode,
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_FILTER_MODE, default=DEFAULT_FILTER_MODE): vol.In(
                        FILTER_MODES
                    ),
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL_SECONDS,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL_SECONDS),
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ParcelAppOptionsFlow(config_entry)


class ParcelAppOptionsFlow(config_entries.OptionsFlow):
    """Handle ParcelApp options."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """Manage ParcelApp options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_FILTER_MODE: user_input[CONF_FILTER_MODE],
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                },
            )

        current_filter_mode = self.config_entry.options.get(
            CONF_FILTER_MODE,
            self.config_entry.data.get(CONF_FILTER_MODE, DEFAULT_FILTER_MODE),
        )
        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(
                CONF_SCAN_INTERVAL,
                DEFAULT_SCAN_INTERVAL_SECONDS,
            ),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FILTER_MODE,
                        default=current_filter_mode,
                    ): vol.In(FILTER_MODES),
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=current_scan_interval,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL_SECONDS),
                    ),
                }
            ),
        )
