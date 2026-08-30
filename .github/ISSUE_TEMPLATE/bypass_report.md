---
name: Bypass report (non-sensitive)
about: A property that should hold but doesn't, and it's safe to discuss publicly
title: "[Bypass] "
labels: bypass
---

> If this is a working bypass you'd rather not publish before there's a
> fix, please use private vulnerability reporting instead (Security tab →
> "Report a vulnerability") per [SECURITY.md](../../SECURITY.md).

Use this template for issues you're comfortable discussing openly, or that
overlap with an already-documented limitation (see the README's "Known
Limitations" section).

**Which property breaks?**
Lineage integrity / conservation / replay protection / signature validity /
audit tamper-evidence / divergence detection.

**Minimal reproduction**
Ideally as a new test in the style of `tests/test_caio.py`.

**Is this the documented issued_at / key-binding / hardcoded-action-list limitation, or something new?**
