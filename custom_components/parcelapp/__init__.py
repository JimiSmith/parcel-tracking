"""The ParcelApp integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ParcelAppApiClient
from .const import CONF_API_KEY, DOMAIN
from .coordinator import ParcelAppDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]
FRONTEND_CARD_FILE = "parcelapp-delivery-card.js"
FRONTEND_CARD_URL = f"/parcelapp_frontend/{FRONTEND_CARD_FILE}"
DATA_FRONTEND_REGISTERED = "_frontend_registered"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the ParcelApp integration."""
    await _async_register_frontend_card(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ParcelApp from a config entry."""
    client = ParcelAppApiClient(async_get_clientsession(hass), entry.data[CONF_API_KEY])
    coordinator = ParcelAppDataUpdateCoordinator(hass, entry, client)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def _async_register_frontend_card(hass: HomeAssistant) -> None:
    """Register the ParcelApp custom delivery card frontend asset."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(DATA_FRONTEND_REGISTERED):
        return

    card_path = Path(__file__).parent / "frontend" / FRONTEND_CARD_FILE
    if not card_path.is_file():
        return

    try:
        from homeassistant.components.http import StaticPathConfig
    except ImportError:
        StaticPathConfig = None

    if hasattr(hass.http, "async_register_static_paths") and StaticPathConfig is not None:
        await hass.http.async_register_static_paths(
            [StaticPathConfig(FRONTEND_CARD_URL, str(card_path), False)]
        )
    elif hasattr(hass.http, "register_static_path"):
        hass.http.register_static_path(FRONTEND_CARD_URL, str(card_path), False)
    else:
        return

    try:
        from homeassistant.components.frontend import add_extra_js_url
    except ImportError:
        return

    add_extra_js_url(hass, FRONTEND_CARD_URL)
    domain_data[DATA_FRONTEND_REGISTERED] = True
