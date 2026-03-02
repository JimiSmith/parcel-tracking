# ParcelApp Deliveries for Home Assistant

A Home Assistant custom integration for tracking ParcelApp deliveries through HACS.

## Requirements

- Parcel premium account with API access.
- API key generated at [https://web.parcelapp.net](https://web.parcelapp.net).

## Installation via HACS

1. Open HACS in Home Assistant.
2. Add this repository as a custom repository of type **Integration**.
3. Install **ParcelApp Deliveries**.
4. Restart Home Assistant.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **ParcelApp Deliveries**.
3. Enter your ParcelApp API key.
4. Choose `filter_mode` (`active` or `recent`) and update interval.

## What gets created

- Summary sensors:
  - `ParcelApp Deliveries`
  - `ParcelApp Out for delivery`
  - `ParcelApp Exceptions`
- One per-delivery sensor per tracking number with status as state and detailed attributes.

## Dynamic dashboard (Auto-Entities)

Install **Auto-Entities** from HACS (Frontend), then add a manual card with:

```yaml
type: custom:auto-entities
card:
  type: entities
  title: ParcelApp Deliveries
show_empty: false
sort:
  method: attribute
  attribute: timestamp_expected
  numeric: true
filter:
  include:
    - domain: sensor
      attributes:
        parcelapp_delivery: true
  exclude:
    - state: unavailable
```

Optional dynamic cards:

```yaml
type: custom:auto-entities
card:
  type: entities
  title: ParcelApp Exceptions
show_empty: false
filter:
  include:
    - domain: sensor
      attributes:
        parcelapp_delivery: true
        status_code: 7
```

## API notes

- Endpoint: `https://api.parcel.app/external/deliveries/`
- Auth header: `api-key`
- API limit: 20 requests/hour (this integration enforces a minimum polling interval).
- Responses are cached by ParcelApp.
