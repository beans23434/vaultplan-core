# Changelog

## [v1.0.4] - 2026-01-20
### Fixed
- [Fix:DB Paths] Documented and aligned DB path expectations across helpers and commands to avoid split SQLite files.
- [Fix:Schema Drift] Labeled schema inconsistencies between init tables and command usage for resolution tracking.
- [Fix:Web3 Columns] Called out mismatched Web3 column names and migrations for cleanup.
- [Fix:Config Duplication] Identified duplicate config access and currency helpers for consolidation.

### Added
#### Safe Phone Update (vaultplan update)
Steps to safely update a phone copy while preserving data:
1. Back up data directory: copy `~/.vaultplan/data/` to a safe location.
2. Run `vaultplan export-summary --mode full --output-dir backups` for a JSON snapshot.
3. Run `vaultplan update` to sync the latest scripts and command modules.
4. Run `vaultplan doctor` to validate tables and apply any migrations.
5. Verify with `vaultplan summary` and `vaultplan balance` before deleting backups.

---

## [v1.0.2] - 2025-05-26
### Fixed
- Crash in `export-summary` due to `saved_amount` renamed to `current_amount`
- Cleaned up duplicated activities in dry runs
- Corrected `note`, `goal`, and `export-summary` commands
- Just honestly clesned my own shit up....
- GumRoad Eddition now includes AI check READMR.md

### Added
- `add-note` and `list-notes` now stable
- Weekly export JSON output confirmed working

---

## [v1.0.1] - 2025-05-25
- CLI no longer crashes on startup
- Initial hotfix from first user feedback
