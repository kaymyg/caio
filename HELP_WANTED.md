# Help wanted

CAIO is open to contributions. Below is the hardening work that would make it stronger, roughly in order of impact. Pick anything, comment on (or open) an issue so others know you are on it, and see [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

Found a vulnerability instead? Please report it privately, see [SECURITY.md](SECURITY.md).


### Validate `Lease.issued_at`

**Medium.** Listed as a known limitation in SECURITY.md: reject leases issued in the future or too far in the past.

### Real challenge-response key binding

**High impact.** Replace the local consistency check with a network challenge-response protocol, with tests.

### General divergence detection

**Medium.** Host divergence detection checks two hardcoded action strings. Make it configurable and test it against new patterns.
