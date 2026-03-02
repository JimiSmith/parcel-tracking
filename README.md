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

Install **Auto-Entities** from HACS (Frontend), then use the dashboard example from `examples/parcelapp-dashboard.yaml`.

## Delivery event attributes

Each per-delivery sensor exposes:

- `latest_event`
- `latest_event_date`
- `latest_event_location`
- `events` (full event list from ParcelApp)

You can inspect these in **Developer Tools → States** on any `sensor.parcelapp_*` delivery entity.

The current example dashboard uses one **sections** view with:
- header + summary badges
- Active Deliveries + Delivery Exceptions auto-entity cards
- a full-width events-by-parcel markdown section

```yaml
views:
  - type: sections
    sections:
      - type: grid
        cards:
          - type: custom:auto-entities
            card:
              type: entities
              title: Active Deliveries
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
          - type: custom:auto-entities
            card:
              type: entities
              title: Delivery Exceptions
            show_empty: false
            filter:
              include:
                - domain: sensor
                  attributes:
                    parcelapp_delivery: true
                    status_code: 7
      - type: grid
        cards:
          - type: markdown
            content: >-
              {% set ns = namespace(deliveries=[]) %}

              {% for s in states.sensor %}
                {% if state_attr(s.entity_id, 'parcelapp_delivery') %}
                  {% set ns.deliveries = ns.deliveries + [s] %}
                {% endif %}
              {% endfor %}

              {% if ns.deliveries | count == 0 %}

              No delivery events yet.

              {% else %}

              {% for s in ns.deliveries | sort(attribute='name') %}

              ## {{ s.name }}

              {% set events = state_attr(s.entity_id, 'events') or [] %}

              {% if events | count == 0 %}

              _No events yet._

              {% else %}

              {% for e in events %}

              - {{ e.get('date') or 'No date' }} — **{{ e.get('event') or 'No
              event' }}**{% if e.get('location') %} ({{ e.get('location') }}){%
              endif %}

              {% endfor %}

              {% endif %}

              {% if not loop.last %}

              ---

              {% endif %}

              {% endfor %}

              {% endif %}
            grid_options:
              columns: full
              rows: auto
        column_span: 2
    header:
      card:
        type: markdown
        text_only: true
        content: Deliveries
    badges:
      - type: entity
        entity: sensor.parcelapp_deliveries
      - type: entity
        entity: sensor.parcelapp_out_for_delivery
      - type: entity
        entity: sensor.parcelapp_exceptions
```

## API notes

- Endpoint: `https://api.parcel.app/external/deliveries/`
- Auth header: `api-key`
- API limit: 20 requests/hour (this integration enforces a minimum polling interval).
- Responses are cached by ParcelApp.
