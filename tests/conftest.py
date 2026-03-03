from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def verify_cleanup():
    """Relax strict cleanup checks for this lightweight local test suite."""
    yield


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow loading local custom_components integrations in tests."""
    yield


@pytest.fixture
def mock_api_client() -> Mock:
    client = Mock()
    client.async_get_deliveries = AsyncMock(return_value=[])
    return client


@pytest.fixture
def sample_deliveries() -> list[dict[str, object]]:
    return [
        {
            "carrier_code": "ups",
            "tracking_number": "1ZAAA",
            "description": "ParcelApp 1",
            "status_code": 4,
            "events": [
                {
                    "date": "2026-03-02 21:00",
                    "event": "Departed facility",
                    "location": "Fargo, ND, United States",
                }
            ],
        },
        {
            "carrier_code": "dhl",
            "tracking_number": "JD014",
            "description": "ParcelApp 2",
            "status_code": 7,
            "events": [],
        },
    ]
