# Security Policy

## Scope

CAIO is a **reference prototype**, not production security software (the
README says so explicitly, and means it). It's small and dense enough to
read in full in one sitting — that's a deliberate design choice, and part
of the point is that the whole trust boundary is auditable at a glance.

What **is** a genuine finding here:

- A way to forge or extend a `Lineage` chain without the parent's private
  key, or make `Lineage.verify()` return `True` for a tampered chain
- A way to make `Ledger.delegate()` allocate more resources to children
  than the parent actually had (breaking conservation)
- A way to reuse a `Lease` nonce and pass `Gateway.transact()`'s replay
  check a second time
- A way to make `Gateway.valid()` accept a lease whose signature doesn't
  actually match its payload
- A way to make `Audit.verify()` return `True` after a log entry has been
  altered, reordered, or deleted
- A way to get `EvidenceGraph.evaluate()` to under-classify a genuinely
  divergent claim/host/network pattern (i.e., something that should reach
  at least `CAPABILITY_REDUCTION` but doesn't)

What's a **known limitation, not a new finding** (see the README and
CONTRIBUTING.md before reporting):

- The agent key-binding check is a local consistency check, not a real
  network challenge-response protocol
- `Lease.issued_at` isn't validated, only `expires_at`
- Host-divergence detection checks two specific hardcoded action strings,
  not general anomaly detection
- Everything is in-memory; nothing here is persisted or distributed

## Reporting

Please **do not** open a public GitHub issue for a working bypass of any of
the properties above — that publishes the technique before there's a fix.

Instead, use GitHub's private vulnerability reporting for this repository
(Security tab → "Report a vulnerability"). Please include:

- A minimal reproduction, ideally as a new test in the style of
  `tests/test_caio.py`
- Which property it breaks (lineage integrity, conservation, replay
  protection, signature validity, audit tamper-evidence, or divergence
  detection)

## Response expectations

Independent reference project — best-effort response, not a guaranteed
SLA. Genuine findings will be prioritized and credited (with permission)
once fixed.
