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

## Dashboard examples

Install **Auto-Entities** from HACS (Frontend), then use one of:

- `examples/parcelapp-dashboard.yaml` (classic entities + markdown events)
- `examples/parcelapp-delivery-cards.yaml` (screenshot-style custom delivery cards)

## Custom delivery card

This integration ships a Lovelace custom card:

- Type: `custom:parcelapp-delivery-card`
- Resource: auto-registered by the integration on startup

If your Home Assistant version does not auto-load it, add this Dashboard resource manually:

- URL: `/parcelapp_frontend/parcelapp-delivery-card.js`
- Type: `JavaScript Module`

### Card options

- `entity` (required): ParcelApp delivery sensor (for example `sensor.parcelapp_ups_...`)
- `title` (optional): override title text
- `events_limit` (optional, default `5`): number of events to show
- `show_expected` (optional, default `true`): show expected delivery window
- `show_carrier` (optional, default `true`): include carrier in title
- `collapsible_events` (optional, default `false`): show all events in expandable block

### Example card

```yaml
type: custom:parcelapp-delivery-card
entity: sensor.parcelapp_ups_1z123456789
events_limit: 5
show_expected: true
show_carrier: true
```

## Delivery event attributes

Each per-delivery sensor exposes:

- `latest_event`
- `latest_event_date`
- `latest_event_location`
- `events` (full event list from ParcelApp)

You can inspect these in **Developer Tools → States** on any `sensor.parcelapp_*` delivery entity.

## API notes

- Endpoint: `https://api.parcel.app/external/deliveries/`
- Auth header: `api-key`
- API limit: 20 requests/hour (this integration enforces a minimum polling interval).
- Responses are cached by ParcelApp.
