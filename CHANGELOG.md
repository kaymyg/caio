# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.3.0] - 2026-08-30

First tagged release. Version matches the prototype's own `__version__`.

### Added

- `LineageChain`: hash-linked, Ed25519-signed ancestry from a human root
  through devices/runtimes to individual agents.
- `Ledger`: thread-safe capability/resource delegation with conservation
  enforcement (no double-spending a parent's budget across children).
- `Lease`: signed, time-boxed, nonce-scoped capability grant with replay
  protection.
- `EvidenceGraph` / `Level`: multi-perspective (claim / host / network)
  divergence detection with graduated escalation (NORMAL → OBSERVATION →
  CAPABILITY_REDUCTION → NETWORK_RESTRICTION → QUARANTINE → TERMINATED).
- `Audit`: hash-chained, tamper-evident log of lease issuance and
  evaluation events.
- `Gateway`: end-to-end `transact()` call tying all of the above together.
- `caio/demo.py`: end-to-end demonstration script.
- Initial test suite (5 tests): lineage tamper detection, ledger
  conservation/double-spend rejection, replay rejection, defense-level
  escalation to TERMINATED, audit tamper-evidence.
- CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, issue templates
  (including a bypass-report template), PR template, Dependabot.
- `pyproject.toml` for proper editable/pip installation (previously only a
  bare `requirements.txt` with no packaging metadata).
- CI: pytest with coverage + demo smoke test across Python 3.10–3.12.

### Fixed

- Expanded test coverage from 5 to 10 tests, closing real gaps found via
  `pytest --cov` (not just added for count): `Gateway.transact()`'s
  expired-lease rejection, tampered-signature rejection, and network-fuel
  exhaustion (429) branches were previously unexercised entirely (0%
  coverage on those lines), and defense-level escalation was only tested
  via `EvidenceGraph.evaluate()` directly, never through `transact()`'s own
  HTTP-style status mapping. `caio/core.py` is now at 100% line coverage.
- Split `requirements.txt` (runtime: `cryptography` only) from
  `requirements-dev.txt` (adds `pytest`, `pytest-cov`) — the original file
  mixed a runtime and a test-only dependency together.

### Notes

- An earlier, more verbose rewrite of this prototype was proposed in a
  prior conversation but was **not** adopted as the basis for this release
  — it dropped real security-relevant features present in the actual
  working prototype (nonce-based replay protection, the hash-chained audit
  log, thread-safety locking) in exchange for more verbose code. This
  release builds on the original, more complete implementation instead.
