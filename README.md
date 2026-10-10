# CAIO — Cryptographically Attested Internet Overlay

[![CI](https://github.com/kaymyg/caio/actions/workflows/ci.yml/badge.svg)](https://github.com/kaymyg/caio/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-10%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25%20core.py-brightgreen)](tests/)
[![CodeQL](https://github.com/kaymyg/caio/actions/workflows/codeql.yml/badge.svg)](https://github.com/kaymyg/caio/actions/workflows/codeql.yml)

A small, dense reference prototype for one question: **when an autonomous
agent acts on a network, how do you cryptographically prove who it is,
what it's allowed to do, and whether it's telling the truth about what it
actually did?**

> ⚠️ **Reference prototype, not production security software.** Deliberately
> small enough to read in full in one sitting (~110 lines of actual logic).
> See "Known Limitations" below before using this for anything real.

## Quick start

```bash
git clone https://github.com/kaymyg/caio.git
cd caio
pip install -r requirements-dev.txt
pip install -e .

python -m caio.demo   # see it work end to end
pytest -q --cov=caio --cov-report=term-missing
```

Expected demo output:

```
Lineage verified: True
Valid transaction: {'status': 200, 'level': 'NORMAL', 'route': 'VERIFIED_OVERLAY'}
Divergence attack: {'status': 500, 'reason': 'terminated'}
Audit verified: True
```

## What it actually does

Six small components, each independently testable:

* **`LineageChain`** — a hash-linked, Ed25519-signed chain from a human
  root through devices/runtimes down to individual agents and sub-agents.
  Each link is signed by its *parent*, so a node can't fabricate its own
  ancestry. `verify()` walks the whole chain and catches any tampered node
  or forged signature.
* **`Ledger`** — capability/resource delegation with real conservation: a
  parent can only delegate compute/network/child-creation budget it
  actually has, and delegating debits the parent atomically (thread-safe
  via `RLock`). No double-spending a budget across two children.
* **`Lease`** — a signed, time-boxed, nonce-scoped capability grant listing
  exactly which capabilities and endpoints an agent may use. Replay is
  blocked by tracking spent nonces; tampering is blocked because the
  signature covers the full canonical payload.
* **`EvidenceGraph` / `Level`** — the core idea: collect what the agent
  *claims* it did, what the *host* independently observed, and what the
  *network* independently observed, then check whether they agree. A
  generic mismatch escalates to `CAPABILITY_REDUCTION`; specific dangerous
  host actions escalate straight to `QUARANTINE`; a disallowed network
  target escalates to `NETWORK_RESTRICTION`; host and network violations
  together escalate to `TERMINATED`.
* **`Audit`** — a hash-chained, tamper-evident log (`prev` + `hash` per
  entry, same shape as a blockchain's block-linking) of every lease
  issuance and evaluation. `verify()` detects any alteration, reordering,
  or deletion.
* **`Gateway`** — ties all of the above together into one call:
  `transact()` validates the lease, checks replay, checks agent
  key-binding, records evidence from all three perspectives, evaluates the
  defense level, and returns an HTTP-style status.

## Relationship to other projects

CAIO isn't a from-scratch idea — it's a deliberate synthesis of mechanisms
already built and independently tested across several sibling projects.
Each one validated a piece of this in isolation:

| Mechanism in CAIO | Proven independently in |
| --- | --- |
| Signed capability leases with trust-state gating | [`ubda-engine`](https://github.com/kaymyg/ubda-engine) — Data Access Capabilities, trust-state thresholds |
| Graduated escalation on breach (not binary allow/deny) | [`hydra-cage`](https://github.com/kaymyg/hydra-cage) — five-plane containment, eight-stage breach transition |
| Multi-perspective divergence detection (claim vs. reality) | [`multi-agent-mcl`](https://github.com/kaymyg/multi-agent-mcl) — behavioral vs. actual policy vector comparison |
| Risk-scored gating before an action executes | [`lean-agent-governance`](https://github.com/kaymyg/lean-agent-governance) — pre-runtime prompt/diff risk scoring |
| Hash-chained, independently-verifiable integrity | [`kaysentinel`](https://github.com/kaymyg/kaysentinel) — canonical hashing, structural + semantic verification gates |

CAIO takes the smallest working version of each of those ideas and wires
them into one coherent request path (`Gateway.transact()`), rather than
five separate systems. It's meant to be the concrete answer to "what would
it look like if these five ideas had to cooperate in a single call."

## Known Limitations

Stated plainly rather than buried, since that's the standard the rest of
this account's projects hold themselves to:

* **The agent key-binding check is a local consistency check, not a real
  network challenge-response protocol.** `Gateway.transact()` signs a
  freshly generated nonce with the `agent_private_key` passed directly into
  the call and immediately verifies it — this proves internal consistency
  (the key matches what the lease claims), not that the request travelled
  over an authenticated channel. A real deployment needs an actual
  challenge issued over the wire.
* **`Lease.issued_at` is never validated**, only `expires_at`. A lease
  claiming to be issued in the future still passes `Gateway.valid()`.
* **Host-divergence detection checks two hardcoded action strings**
  (`CRITICAL_TAMPER`, `UNSANCTIONED_EXEC`), not general anomaly detection.
  Any other kind of claim/host mismatch reaches `CAPABILITY_REDUCTION` at
  most, not `QUARANTINE` — that's intentional graduated response, not a
  bug, but it means the detector's actual coverage is narrower than
  "catches divergence" might suggest at a glance.
* **Everything is in-memory.** `Ledger`, `Audit`, and `EvidenceGraph` state
  don't survive a process restart; there's no persistence layer.
* **Single-process only.** No distributed consensus on lineage, ledger
  balances, or audit log state across multiple gateway instances.

## Contributing

Bug reports, new divergence scenarios, and PRs are welcome — see
[`CONTRIBUTING.md`](CONTRIBUTING.md) for setup and what CI checks.

## Security

Found a way to forge lineage, double-spend a ledger balance, replay a
nonce, or make the audit log lie about tampering? Please see
[`SECURITY.md`](SECURITY.md) for how to report it responsibly rather than
opening a public issue.

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).

## License

MIT — see [`LICENSE`](LICENSE).
