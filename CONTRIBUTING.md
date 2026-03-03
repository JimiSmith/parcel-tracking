# Contributing

## Local setup

1. `make setup`
2. `source .venv/bin/activate`
3. Configure/test in Home Assistant as needed.

## Daily workflow

- Run lint: `make lint`
- Run tests: `make test`
- Run full local gate before commit: `make check`

## Test focus

- API client behavior and error mapping
- Coordinator refresh behavior and option normalization
- Sensor lifecycle, stale registry cleanup, and device grouping
- Config flow success and error paths

## Troubleshooting

- If tools are missing, re-run `make setup`.
- If Home Assistant test dependencies changed, remove `.venv` and run `make setup` again.
