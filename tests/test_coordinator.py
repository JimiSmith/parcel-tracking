from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from custom_components.parcelapp.api import ParcelAppApiAuthError, ParcelAppApiError
from custom_components.parcelapp.const import (
    CONF_FILTER_MODE,
    CONF_SCAN_INTERVAL,
    DEFAULT_FILTER_MODE,
    MIN_SCAN_INTERVAL_SECONDS,
)
from custom_components.parcelapp.coordinator import ParcelAppDataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry


def _make_entry(**data) -> MockConfigEntry:
    return MockConfigEntry(domain="parcelapp", data=data)


def test_filter_mode_defaults_when_invalid(hass) -> None:
    entry = _make_entry(api_key="key", filter_mode="invalid", scan_interval=900)
    api_client = AsyncMock()
    coordinator = ParcelAppDataUpdateCoordinator(hass, entry, api_client)

    assert coordinator.filter_mode == DEFAULT_FILTER_MODE


def test_scan_interval_respects_minimum(hass) -> None:
    entry = _make_entry(
        api_key="key",
        filter_mode="active",
        scan_interval=MIN_SCAN_INTERVAL_SECONDS - 10,
    )
    api_client = AsyncMock()
    coordinator = ParcelAppDataUpdateCoordinator(hass, entry, api_client)

    assert coordinator.scan_interval_seconds == MIN_SCAN_INTERVAL_SECONDS


@pytest.mark.asyncio
async def test_update_data_raises_auth_failed(hass) -> None:
    entry = _make_entry(api_key="key", filter_mode="active", scan_interval=900)
    api_client = AsyncMock()
    api_client.async_get_deliveries.side_effect = ParcelAppApiAuthError("bad key")
    coordinator = ParcelAppDataUpdateCoordinator(hass, entry, api_client)

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_update_data_raises_update_failed(hass) -> None:
    entry = _make_entry(api_key="key", filter_mode="active", scan_interval=900)
    api_client = AsyncMock()
    api_client.async_get_deliveries.side_effect = ParcelAppApiError("api failure")
    coordinator = ParcelAppDataUpdateCoordinator(hass, entry, api_client)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_update_data_returns_deliveries(hass) -> None:
    entry = _make_entry(api_key="key", filter_mode="active", scan_interval=900)
    api_client = AsyncMock()
    api_client.async_get_deliveries.return_value = [{"tracking_number": "1Z"}]
    coordinator = ParcelAppDataUpdateCoordinator(hass, entry, api_client)

    result = await coordinator._async_update_data()

    assert result == {"deliveries": [{"tracking_number": "1Z"}]}
    api_client.async_get_deliveries.assert_awaited_once_with("active")


def test_options_override_entry_data(hass) -> None:
    entry = MockConfigEntry(
        domain="parcelapp",
        data={"api_key": "key", "filter_mode": "active", "scan_interval": 900},
        options={CONF_FILTER_MODE: "recent", CONF_SCAN_INTERVAL: 1200},
    )
    api_client = AsyncMock()
    coordinator = ParcelAppDataUpdateCoordinator(hass, entry, api_client)

    assert coordinator.filter_mode == "recent"
    assert coordinator.scan_interval_seconds == 1200
