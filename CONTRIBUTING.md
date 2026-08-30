# Contributing to CAIO

Thanks for your interest. CAIO is a reference prototype synthesizing ideas
validated separately across several sibling projects (see the README's
"Relationship to other projects" section) — contributions that strengthen
the actual security properties (lineage integrity, capability conservation,
divergence detection, audit tamper-evidence) are especially valuable.

## Getting set up

```bash
git clone https://github.com/kaymyg/caio.git
cd caio
pip install -r requirements-dev.txt
pip install -e .

python -m caio.demo   # see it work end to end
pytest -q --cov=caio --cov-report=term-missing   # 10 tests, 100% on core.py
```

## Before opening a PR

CI runs the test suite with coverage and the demo script, across Python
3.10–3.12, on every push and PR. Please run that locally first.

If you add a new branch or status code to `Gateway.transact()`, add a test
that exercises it through `gw.transact()` itself, not just the underlying
helper it calls — `test_transact_level_status_mapping` exists specifically
because the original test suite covered `EvidenceGraph.evaluate()` directly
but never asserted what `transact()` actually mapped that result to.

## What especially matters here

- **This is a reference prototype, not a deployable network protocol.** The
  agent key-binding check in `Gateway.transact()` is a local
  sign/verify-with-a-fresh-nonce consistency check, not a real challenge
  issued over an untrusted wire — be precise about this distinction in any
  docs or code you touch, don't let it get oversold.
- **`Lease.expires_at` is checked; `Lease.issued_at` is not.** A lease
  "valid" from a future timestamp still passes `Gateway.valid()`. This is a
  known, documented gap (see README "Known Limitations"), not an oversight
  to silently patch — if you fix it, make sure you understand why it was
  left out (clock-skew tolerance) before tightening it.
- **The host-divergence detector checks two specific action strings**
  (`CRITICAL_TAMPER`, `UNSANCTIONED_EXEC`), not general anomaly detection.
  A generic claim/host mismatch only reaches `CAPABILITY_REDUCTION`, not
  `QUARANTINE` — that's intentional graduated response, not a bug, but
  don't describe it as catching "any divergence" in docs.
- **Nonce replay protection burns the nonce only after key-binding
  succeeds** — preserve that ordering if you touch `transact()`; marking a
  nonce used before authentication would let an attacker burn a legitimate
  agent's nonce with a failed forged request.

## Good places to start

- A real network-level challenge-response protocol to replace the local
  key-binding consistency check
- `issued_at` validation (with configurable clock-skew tolerance)
- Persisting `Ledger`/`Audit`/`EvidenceGraph` state instead of in-memory only
- Expanding the host-action taxonomy beyond the current two hardcoded
  "bad" actions, ideally via a configurable policy rather than more
  hardcoded strings
- A real transport binding (HTTP middleware, gRPC interceptor) around
  `Gateway.transact()`

For anything larger, please open an issue first to discuss the approach.

## Commit style

Small, focused commits with a clear one-line summary. No strict format
enforced beyond that.
