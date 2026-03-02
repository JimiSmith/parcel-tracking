"""Sensors for ParcelApp deliveries."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_LABELS
from .coordinator import ParcelAppDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ParcelApp sensors from a config entry."""
    coordinator: ParcelAppDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    summary_entities: list[SensorEntity] = [
        ParcelSummarySensor(
            coordinator,
            entry.entry_id,
            "deliveries_count",
            "Deliveries",
            "mdi:package-variant",
            lambda deliveries: len(deliveries),
        ),
        ParcelSummarySensor(
            coordinator,
            entry.entry_id,
            "out_for_delivery_count",
            "Out for delivery",
            "mdi:truck-delivery",
            lambda deliveries: sum(
                1 for delivery in deliveries if delivery.get("status_code") == 4
            ),
        ),
        ParcelSummarySensor(
            coordinator,
            entry.entry_id,
            "exception_count",
            "Exceptions",
            "mdi:alert-circle",
            lambda deliveries: sum(
                1
                for delivery in deliveries
                if delivery.get("status_code") in (6, 7)
            ),
        ),
    ]

    delivery_entities: dict[str, ParcelDeliverySensor] = {}

    @callback
    def _sync_delivery_entities() -> None:
        deliveries = _get_deliveries(coordinator)
        current_keys: set[str] = set()
        new_entities: list[SensorEntity] = []

        for delivery in deliveries:
            delivery_key = _delivery_key(delivery)
            if delivery_key is None:
                continue

            current_keys.add(delivery_key)
            if delivery_key in delivery_entities:
                continue

            entity = ParcelDeliverySensor(coordinator, entry.entry_id, delivery_key)
            delivery_entities[delivery_key] = entity
            new_entities.append(entity)

        removed = set(delivery_entities) - current_keys
        for delivery_key in removed:
            entity = delivery_entities.pop(delivery_key)
            hass.async_create_task(entity.async_remove())

        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(_sync_delivery_entities))

    async_add_entities(summary_entities)
    _sync_delivery_entities()


class ParcelSummarySensor(CoordinatorEntity[ParcelAppDataUpdateCoordinator], SensorEntity):
    """Summary sensor based on ParcelApp deliveries."""

    def __init__(
        self,
        coordinator: ParcelAppDataUpdateCoordinator,
        entry_id: str,
        sensor_key: str,
        name: str,
        icon: str,
        calculator: Callable[[list[dict[str, Any]]], int],
    ) -> None:
        super().__init__(coordinator)
        self._calculator = calculator
        self._attr_name = f"ParcelApp {name}"
        self._attr_unique_id = f"{entry_id}_{sensor_key}"
        self._attr_icon = icon

    @property
    def native_value(self) -> int:
        """Return the sensor value."""
        return self._calculator(_get_deliveries(self.coordinator))


class ParcelDeliverySensor(CoordinatorEntity[ParcelAppDataUpdateCoordinator], SensorEntity):
    """A sensor for a single ParcelApp delivery."""

    def __init__(
        self,
        coordinator: ParcelAppDataUpdateCoordinator,
        entry_id: str,
        delivery_key: str,
    ) -> None:
        super().__init__(coordinator)
        self._delivery_key = delivery_key
        self._attr_unique_id = f"{entry_id}_{delivery_key}"
        self._attr_icon = "mdi:package-variant-closed"

    @property
    def name(self) -> str:
        """Return the sensor name."""
        delivery = self._delivery
        if delivery is None:
            return f"ParcelApp {self._delivery_key}"

        description = delivery.get("description") or delivery.get("tracking_number")
        return f"ParcelApp {description}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._delivery is not None

    @property
    def native_value(self) -> str | None:
        """Return the delivery status text."""
        delivery = self._delivery
        if delivery is None:
            return None

        status_code = delivery.get("status_code")
        if isinstance(status_code, int):
            return STATUS_LABELS.get(status_code, f"Unknown ({status_code})")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes for the delivery."""
        delivery = self._delivery
        if delivery is None:
            return {}

        events = delivery.get("events") or []
        latest_event = events[0] if events else {}

        return {
            "carrier_code": delivery.get("carrier_code"),
            "tracking_number": delivery.get("tracking_number"),
            "description": delivery.get("description"),
            "status_code": delivery.get("status_code"),
            "extra_information": delivery.get("extra_information"),
            "date_expected": delivery.get("date_expected"),
            "date_expected_end": delivery.get("date_expected_end"),
            "timestamp_expected": delivery.get("timestamp_expected"),
            "timestamp_expected_end": delivery.get("timestamp_expected_end"),
            "latest_event": latest_event.get("event"),
            "latest_event_date": latest_event.get("date"),
            "latest_event_location": latest_event.get("location"),
            "events": events,
        }

    @property
    def _delivery(self) -> dict[str, Any] | None:
        for delivery in _get_deliveries(self.coordinator):
            if _delivery_key(delivery) == self._delivery_key:
                return delivery
        return None


def _get_deliveries(
    coordinator: ParcelAppDataUpdateCoordinator,
) -> list[dict[str, Any]]:
    data = coordinator.data or {}
    deliveries = data.get("deliveries", [])
    if isinstance(deliveries, list):
        return [delivery for delivery in deliveries if isinstance(delivery, dict)]
    return []


def _delivery_key(delivery: dict[str, Any]) -> str | None:
    tracking_number = delivery.get("tracking_number")
    if not isinstance(tracking_number, str) or not tracking_number:
        return None

    carrier_code = delivery.get("carrier_code")
    carrier = carrier_code if isinstance(carrier_code, str) else "unknown"
    return f"{carrier}:{tracking_number}"
