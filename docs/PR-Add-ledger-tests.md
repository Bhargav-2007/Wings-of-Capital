Title: tests(ledger): add reporting, routes, and edge-case ledger tests

Summary
-------
This branch adds comprehensive ledger tests (reporting, route integration, and edge-cases) and a
few small compatibility fixes required to run the test-suite reliably under an in-memory SQLite test
environment and Pydantic v2.

Files changed (high level)
- backend/services/ledger_service/tests/test_reports.py  (new)
- backend/services/ledger_service/tests/test_edgecases.py (new)
- backend/services/ledger_service/tests/test_routes.py   (added earlier)
- backend/services/ledger_service/ledger/reporting.py  (fixed as-of-date calculations)
- backend/services/ledger_service/routes/reports.py    (balance-sheet behavior)
- backend/services/ledger_service/schemas/transactions.py (allow UUID outputs)
- backend/services/shared/config.py                    (settings: allow constructor inputs)
- backend/services/shared/db_types.py                  (UUID TypeDecorator)
- backend/services/shared/database.py                  (sqlite engine compatibility)

Why
---
- Improve ledger coverage: trial balance, income statement, balance sheet
- Add edge-cases: multi-currency rejection, allow_negative behavior, as-of-date balances
- Make tests reliably runnable in CI (SQLite in-memory tests)

How to run locally
-------------------
```bash
source .venv/bin/activate
pytest -q
```

Suggested branch & commit
-------------------------
- Branch: `feat/ledger-tests`
- Commit message: `tests(ledger): add reporting, routes, and edge-case tests; reporting fixes`

Create PR (example commands)
-----------------------------
```bash
git checkout -b feat/ledger-tests
git add -A
git commit -m "tests(ledger): add reporting, routes, and edge-case tests; reporting fixes"
git push --set-upstream origin feat/ledger-tests
gh pr create --title "tests(ledger): add reporting & edge-case tests" --body-file docs/PR-Add-ledger-tests.md --base main
```

Notes
-----
- There are a few small, targeted changes to `shared.config` and `ledger_service.reporting` to keep
  backward compatibility between environment-loaded and constructor-provided settings, and to compute
  historical balances correctly when tests seed account balances and then add dated transactions.
- If you want, I can open the PR for you (I need push/remote access) or provide the exact git/gh commands
  to run locally.
