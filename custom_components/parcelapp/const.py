"""Constants for the ParcelApp integration."""

from homeassistant.const import CONF_API_KEY

DOMAIN = "parcelapp"
TITLE = "ParcelApp"

CONF_FILTER_MODE = "filter_mode"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_FILTER_MODE = "active"
DEFAULT_SCAN_INTERVAL_SECONDS = 900
MIN_SCAN_INTERVAL_SECONDS = 300

FILTER_MODES: tuple[str, str] = ("active", "recent")

API_DELIVERIES_URL = "https://api.parcel.app/external/deliveries/"

STATUS_LABELS: dict[int, str] = {
    0: "Delivered",
    1: "Frozen",
    2: "In transit",
    3: "Pickup required",
    4: "Out for delivery",
    5: "Not found",
    6: "Failed attempt",
    7: "Exception",
    8: "Info received",
}

__all__ = [
    "API_DELIVERIES_URL",
    "CONF_API_KEY",
    "CONF_FILTER_MODE",
    "CONF_SCAN_INTERVAL",
    "DEFAULT_FILTER_MODE",
    "DEFAULT_SCAN_INTERVAL_SECONDS",
    "DOMAIN",
    "FILTER_MODES",
    "MIN_SCAN_INTERVAL_SECONDS",
    "STATUS_LABELS",
    "TITLE",
]
