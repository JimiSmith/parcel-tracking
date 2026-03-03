# AGENTS.md

## Project Scope
- Home Assistant custom integration: `custom_components/parcelapp`
- Frontend custom card: `custom_components/parcelapp/frontend/parcelapp-delivery-card.js`

## Daily Commands
- Tests: `pytest -q`
- Lint: `ruff check custom_components tests`

## Release Checklist (Frequent)
1. Bump integration version in `custom_components/parcelapp/manifest.json`.
2. If frontend card JS changed, bump `FRONTEND_CARD_CACHE_TOKEN` in `custom_components/parcelapp/__init__.py`.
3. Commit and push to `main`.

## Frontend Card Notes
- Card type: `custom:parcelapp-delivery-card`
- Auto-registration is done in `custom_components/parcelapp/__init__.py`.
- Static path: `/parcelapp_frontend/parcelapp-delivery-card.js`
- Resource URL uses cache busting: `/parcelapp_frontend/parcelapp-delivery-card.js?v=<token>`

## Common Dashboard Pitfall
When using `custom:auto-entities`, the card must receive the generated entity explicitly:

```yaml
options:
  type: custom:parcelapp-delivery-card
  entity: this.entity_id
```

Without this, cards may show "Configuration error".

## Debugging Quick Checks
- Verify element loaded in browser console:
  - `customElements.get('parcelapp-delivery-card')`
- Verify resource fetched:
  - `performance.getEntriesByType('resource').map(r => r.name).filter(n => n.includes('parcelapp-delivery-card'))`
