# H114/H115 — local indistinguishability funnel

## Status

`OPEN`, reproducibility `R1`.

C014 made H106 falsifiable by restricting a compiler to a constant number of
bounded-radius passes. C015 now fixes the exact lower-bound shape needed to
attack that class.

## Required hard pair

For fixed constants `q,r`, construct explicit signed CNF families

```text
SAT_n, UNSAT_n
```

with opposite satisfiability such that the multisets of rooted signed incidence
neighborhoods agree exactly through radius `q r`.

Equality must include:

- variable versus clause node types;
- literal signs on incidence edges;
- rooted isomorphism type;
- multiplicity of every type.

High girth is a construction aid, not a substitute for exact equality.

## Why this attacks H106

Every output symbol of an H106 compiler has ancestry inside one radius-`qr`
input neighborhood. For an isomorphism-invariant finite interpretation, equal
input neighborhood-type inventories strongly constrain the output symbols and
all local recovery annotations.

However, equal local inventories alone do not force globally isomorphic output
graphs. H115 therefore isolates a separate transfer theorem:

1. formalize the compiler as a finite interpretation;
2. include all recovery annotations in the interpretation;
3. prove that O(log n)-treewidth output can be canonically decomposed, or that
   the dynamic program is invariant under decomposition choice;
4. prove that the resulting decision and recovery transcript is determined by
   the interpreted type data.

Only after this theorem may opposite SAT labels yield a contradiction.

## Principal attacks

### Global assembly

Locally identical pieces can assemble into globally different graphs. A proof
must control assembly, not merely node colors.

### Multiplicity leakage

A compiler may count local types. H114 requires equal multisets, not only equal
sets of neighborhood types.

### Recovery leakage

A witness-recovery procedure may carry nonlocal information. Every annotation,
merge operation, and scheduler state must be charged to the H106 ancestry
restriction.

### Opposite-label construction

The main missing object is an explicit SAT/UNSAT pair satisfying exact local
identity. Random lifts or covering arguments are not accepted without a
deterministic construction and proof of both labels.

## Executable audit

```bash
python experiments/direct/local_neighborhood_audit.py --self-test
```

The tool exactly computes finite rooted signed-neighborhood signatures and
checks variable-renaming invariance on fixtures. It neither constructs H114 nor
proves the H115 transfer.

## Claim boundary

This funnel can destroy only the restricted constant-pass compiler class H106.
It is not a lower bound against arbitrary polynomial-time algorithms and does
not by itself imply `P != NP`.
