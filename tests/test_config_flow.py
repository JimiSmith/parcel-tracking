from __future__ import annotations

from unittest.mock import patch

import pytest
from custom_components.parcelapp.api import ParcelAppApiAuthError, ParcelAppApiError
from custom_components.parcelapp.const import DOMAIN
from homeassistant import config_entries


@pytest.mark.asyncio
async def test_user_flow_creates_entry(hass) -> None:
    user_input = {
        "api_key": "test-key",
        "filter_mode": "active",
        "scan_interval": 900,
    }

    with patch(
        "custom_components.parcelapp.config_flow.ParcelAppApiClient.async_get_deliveries",
        return_value=[],
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data=user_input,
        )

    assert result["type"] == "create_entry"
    assert result["title"] == "ParcelApp"
    assert result["data"] == user_input


@pytest.mark.asyncio
async def test_user_flow_invalid_auth(hass) -> None:
    user_input = {
        "api_key": "bad-key",
        "filter_mode": "active",
        "scan_interval": 900,
    }

    with patch(
        "custom_components.parcelapp.config_flow.ParcelAppApiClient.async_get_deliveries",
        side_effect=ParcelAppApiAuthError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data=user_input,
        )

    assert result["type"] == "form"
    assert result["errors"] == {"base": "invalid_auth"}


@pytest.mark.asyncio
async def test_user_flow_cannot_connect(hass) -> None:
    user_input = {
        "api_key": "bad-key",
        "filter_mode": "active",
        "scan_interval": 900,
    }

    with patch(
        "custom_components.parcelapp.config_flow.ParcelAppApiClient.async_get_deliveries",
        side_effect=ParcelAppApiError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data=user_input,
        )

    assert result["type"] == "form"
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_options_flow_updates_values(hass) -> None:
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"api_key": "test-key", "filter_mode": "active", "scan_interval": 900},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == "form"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"filter_mode": "recent", "scan_interval": 1200},
    )

    assert result2["type"] == "create_entry"
    assert result2["data"] == {"filter_mode": "recent", "scan_interval": 1200}
