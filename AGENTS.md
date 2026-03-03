# AGENTS.md

## Project Scope
- Home Assistant custom integration: `custom_components/parcelapp`

## Daily Commands
- Tests: `pytest -q`
- Lint: `ruff check custom_components tests`

## Release Checklist (Frequent)
1. Bump integration version in `custom_components/parcelapp/manifest.json`.
2. Commit and push to `main`.

## Frontend Card Plugin
- Custom card is maintained in a separate repository:
  - `https://github.com/JimiSmith/parcelapp-lovelace-card`

## Common Dashboard Pitfall
When using `custom:auto-entities` with `card_param: cards`, each generated item must include a valid `type`.
If you only want default rows, prefer an `entities` card instead of a `grid` card with generated child cards.

## Debugging Quick Checks
- Verify integration entities exist:
  - `sensor.parcelapp_deliveries`
  - per-delivery sensors with `parcelapp_delivery: true`
