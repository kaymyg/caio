## What does this change do?

<!-- Brief description -->

## Checklist

- [ ] `pytest -q --cov=caio --cov-report=term-missing` passes (10 tests,
      100% on `caio/core.py`)
- [ ] `python -m caio.demo` still runs end to end
- [ ] New branches in `Gateway.transact()` are tested through `transact()`
      itself, not just the helper method they call
- [ ] Nonce-burning still happens only after key-binding succeeds, if you
      touched that ordering
- [ ] Updated the README if this changes a documented property, limitation,
      or the architecture

## Related issue

<!-- Closes #123, if applicable -->
