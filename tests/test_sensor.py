from __future__ import annotations

from types import SimpleNamespace

from custom_components.parcelapp.sensor import (
    ParcelDeliverySensor,
    ParcelSummarySensor,
    _delivery_key,
    _get_deliveries,
    _remove_stale_registry_delivery_entities,
)


def _coordinator_with(deliveries: list[dict]) -> SimpleNamespace:
    return SimpleNamespace(data={"deliveries": deliveries})


def test_get_deliveries_filters_non_dict_entries() -> None:
    coordinator = SimpleNamespace(data={"deliveries": [{"tracking_number": "1Z"}, 123]})

    deliveries = _get_deliveries(coordinator)

    assert deliveries == [{"tracking_number": "1Z"}]


def test_delivery_key_uses_carrier_and_tracking() -> None:
    key = _delivery_key({"carrier_code": "ups", "tracking_number": "1ZAAA"})

    assert key == "ups:1ZAAA"


def test_summary_sensor_counts(hass, sample_deliveries) -> None:
    coordinator = _coordinator_with(sample_deliveries)

    deliveries_sensor = ParcelSummarySensor(
        coordinator,
        "entry-1",
        "deliveries_count",
        "Deliveries",
        "mdi:package-variant",
        lambda deliveries: len(deliveries),
    )
    out_for_delivery_sensor = ParcelSummarySensor(
        coordinator,
        "entry-1",
        "out_for_delivery_count",
        "Out for delivery",
        "mdi:truck-delivery",
        lambda deliveries: sum(
            1 for delivery in deliveries if delivery.get("status_code") == 4
        ),
    )

    assert deliveries_sensor.native_value == 2
    assert out_for_delivery_sensor.native_value == 1


def test_delivery_sensor_exposes_expected_attributes(hass, sample_deliveries) -> None:
    coordinator = _coordinator_with(sample_deliveries)
    sensor = ParcelDeliverySensor(coordinator, "entry-1", "ups:1ZAAA")

    assert sensor.native_value == "Out for delivery"
    assert sensor.extra_state_attributes["tracking_number"] == "1ZAAA"
    assert sensor.extra_state_attributes["latest_event"] == "Departed facility"
    assert sensor.device_info["identifiers"] == {("parcelapp", "entry-1")}


def test_remove_stale_registry_delivery_entities(monkeypatch, hass) -> None:
    removed: list[str] = []
    fake_registry = SimpleNamespace(async_remove=lambda entity_id: removed.append(entity_id))

    entries = [
        SimpleNamespace(
            domain="sensor",
            unique_id="entry-1_ups:active",
            entity_id="sensor.parcelapp_active",
        ),
        SimpleNamespace(
            domain="sensor",
            unique_id="entry-1_ups:stale",
            entity_id="sensor.parcelapp_stale",
        ),
        SimpleNamespace(
            domain="sensor",
            unique_id="entry-1_deliveries_count",
            entity_id="sensor.parcelapp_deliveries",
        ),
    ]

    monkeypatch.setattr(
        "custom_components.parcelapp.sensor.er.async_get",
        lambda _hass: fake_registry,
    )
    monkeypatch.setattr(
        "custom_components.parcelapp.sensor.er.async_entries_for_config_entry",
        lambda _registry, _entry_id: entries,
    )

    entry = SimpleNamespace(entry_id="entry-1")
    removed_count = _remove_stale_registry_delivery_entities(
        hass,
        entry,
        {"entry-1_ups:active"},
    )

    assert removed_count == 1
    assert removed == ["sensor.parcelapp_stale"]
