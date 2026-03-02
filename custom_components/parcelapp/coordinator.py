"""Coordinator for ParcelApp data updates."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ParcelAppApiAuthError, ParcelAppApiClient, ParcelAppApiError
from .const import (
    CONF_FILTER_MODE,
    CONF_SCAN_INTERVAL,
    DEFAULT_FILTER_MODE,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DOMAIN,
    MIN_SCAN_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


class ParcelAppDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching ParcelApp data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api_client: ParcelAppApiClient,
    ) -> None:
        self.config_entry = config_entry
        self.api_client = api_client

        update_interval = timedelta(seconds=self.scan_interval_seconds)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    @property
    def filter_mode(self) -> str:
        """Return configured filter mode."""
        value = self.config_entry.options.get(
            CONF_FILTER_MODE,
            self.config_entry.data.get(CONF_FILTER_MODE, DEFAULT_FILTER_MODE),
        )
        if value in ("active", "recent"):
            return value
        return DEFAULT_FILTER_MODE

    @property
    def scan_interval_seconds(self) -> int:
        """Return scan interval, respecting limits."""
        configured = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(
                CONF_SCAN_INTERVAL,
                DEFAULT_SCAN_INTERVAL_SECONDS,
            ),
        )
        try:
            interval = int(configured)
        except (TypeError, ValueError):
            interval = DEFAULT_SCAN_INTERVAL_SECONDS
        return max(interval, MIN_SCAN_INTERVAL_SECONDS)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest data from ParcelApp."""
        try:
            deliveries = await self.api_client.async_get_deliveries(self.filter_mode)
        except ParcelAppApiAuthError as err:
            raise ConfigEntryAuthFailed from err
        except ParcelAppApiError as err:
            raise UpdateFailed(str(err)) from err

        return {"deliveries": deliveries}
