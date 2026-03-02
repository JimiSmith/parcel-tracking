"""API client for ParcelApp."""

from __future__ import annotations

from asyncio import TimeoutError
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import API_DELIVERIES_URL, FILTER_MODES


class ParcelAppApiError(Exception):
    """Base ParcelApp API exception."""


class ParcelAppApiAuthError(ParcelAppApiError):
    """Auth-related ParcelApp API exception."""


class ParcelAppApiClient:
    """Client for the ParcelApp deliveries API."""

    def __init__(self, session: ClientSession, api_key: str) -> None:
        self._session = session
        self._api_key = api_key

    async def async_get_deliveries(self, filter_mode: str) -> list[dict[str, Any]]:
        """Fetch deliveries from ParcelApp."""
        if filter_mode not in FILTER_MODES:
            filter_mode = FILTER_MODES[0]

        try:
            response = await self._session.get(
                API_DELIVERIES_URL,
                headers={"api-key": self._api_key},
                params={"filter_mode": filter_mode},
                timeout=20,
            )
        except (ClientError, TimeoutError) as err:
            raise ParcelAppApiError(f"Network error: {err}") from err

        async with response:
            if response.status in (401, 403):
                raise ParcelAppApiAuthError("Invalid API key")

            if response.status >= 400:
                body = await response.text()
                raise ParcelAppApiError(
                    f"Unexpected HTTP status {response.status}: {body}"
                )

            payload = await response.json(content_type=None)

        if not payload.get("success", False):
            message = payload.get("error_message", "Unknown API error")
            if "api key" in message.lower() or "auth" in message.lower():
                raise ParcelAppApiAuthError(message)
            raise ParcelAppApiError(message)

        deliveries = payload.get("deliveries", [])
        if not isinstance(deliveries, list):
            raise ParcelAppApiError("Invalid deliveries payload")

        return deliveries
