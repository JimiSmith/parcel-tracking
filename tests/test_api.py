from __future__ import annotations

import builtins

import pytest
from custom_components.parcelapp.api import (
    ParcelAppApiAuthError,
    ParcelAppApiClient,
    ParcelAppApiError,
)


class FakeResponse:
    def __init__(self, status: int, payload: dict | None = None, text: str = "") -> None:
        self.status = status
        self._payload = payload or {}
        self._text = text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def json(self, content_type=None):
        return self._payload

    async def text(self):
        return self._text


class FakeSession:
    def __init__(self, response: FakeResponse | Exception) -> None:
        self._response = response

    async def get(self, *args, **kwargs):
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


@pytest.mark.asyncio
async def test_async_get_deliveries_success() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "success": True,
                "deliveries": [{"tracking_number": "1ZAAA"}],
            },
        )
    )
    client = ParcelAppApiClient(session, "key")

    deliveries = await client.async_get_deliveries("active")

    assert deliveries == [{"tracking_number": "1ZAAA"}]


@pytest.mark.asyncio
async def test_async_get_deliveries_auth_error_from_status() -> None:
    session = FakeSession(FakeResponse(401, {"success": False, "error_message": "bad"}))
    client = ParcelAppApiClient(session, "key")

    with pytest.raises(ParcelAppApiAuthError):
        await client.async_get_deliveries("active")


@pytest.mark.asyncio
async def test_async_get_deliveries_auth_error_from_payload_message() -> None:
    session = FakeSession(
        FakeResponse(200, {"success": False, "error_message": "API key invalid"})
    )
    client = ParcelAppApiClient(session, "key")

    with pytest.raises(ParcelAppApiAuthError):
        await client.async_get_deliveries("active")


@pytest.mark.asyncio
async def test_async_get_deliveries_network_error() -> None:
    session = FakeSession(builtins.TimeoutError("timeout"))
    client = ParcelAppApiClient(session, "key")

    with pytest.raises(ParcelAppApiError, match="Network error"):
        await client.async_get_deliveries("active")


@pytest.mark.asyncio
async def test_async_get_deliveries_invalid_payload_shape() -> None:
    session = FakeSession(FakeResponse(200, {"success": True, "deliveries": {}}))
    client = ParcelAppApiClient(session, "key")

    with pytest.raises(ParcelAppApiError, match="Invalid deliveries payload"):
        await client.async_get_deliveries("active")
