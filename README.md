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

Install **Auto-Entities** from HACS (Frontend), then use:

- `examples/parcelapp-dashboard.yaml` (entities + markdown events)

## Optional frontend card plugin

This repository is integration-only.  
If you want the dedicated custom Lovelace card, install the separate frontend plugin:

- `https://github.com/JimiSmith/parcelapp-lovelace-card`

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

## Development

For local development setup and test commands, see `CONTRIBUTING.md`.
