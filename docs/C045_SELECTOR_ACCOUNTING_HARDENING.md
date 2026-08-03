# C045 Selector Accounting Hardening

```text
P_VS_NP = OPEN
C045 = IMPLEMENTED / DRAFT / REVIEW_PENDING
```

This hardening layer closes the remaining selector-envelope obligations without changing the C045 mathematical theorem.

## Fixed-point certificate accounting

The serialized selector certificate contains both its charged ledger and its own stated byte count. C045 therefore iterates the byte count to a fixed point and charges every newly exposed byte exactly once. Exceeding the fixed polynomial capability returns:

```text
OPEN_CERTIFICATE_VOLUME
```

## Independent refusal replay

`janus_c045_basis_portfolio_verifier_v2.py` does not call the C045 producer. It first uses the original independent verifier for exact SAT/UNSAT and ordinary portfolio OPEN terminals. For selector budget refusals it independently reconstructs:

```text
canonical affine basis
frozen candidate manifest
all unique basis transforms
one independent C044 probe per candidate
selector decision and attempted finalization
```

It accepts `OPEN_DISCOVERY_BUDGET` or `OPEN_CERTIFICATE_VOLUME` only when the identical exception, stage, evidence and charged selector ledger are reproduced.

## Added frozen controls

```text
selector work cap 1
-> OPEN_DISCOVERY_BUDGET
-> independent replay ACCEPTED

selector certificate cap 128 bytes
-> OPEN_CERTIFICATE_VOLUME
-> independent replay ACCEPTED

modified refusal evidence
-> REJECTED
```

The hardened frozen audit has digest:

```text
c70ce5c8e605c6dc2516bba37d79f2e14cf62a39bd19ad1ed257420e5337fea0
```

The original frozen audit remains as a semantic-regression gate; the v2 audit is an additional stricter accounting gate.
