# Local certificates for an erroneous SAT circuit

## Purpose

H031 and H056 were blocked by an apparent asymmetry: a false negative can be certified by a satisfying assignment, while a false positive seems to require a general UNSAT certificate.

SAT self-reducibility removes that specific obstacle once one erroneous formula is known.

## Canonical identity

For a CNF `G` and its first unset variable `x`, let `G_0` and `G_1` be the canonically simplified restrictions. With fixed-length padding,

`SAT(G) = SAT(G_0) OR SAT(G_1)`.

## False negative

If a candidate circuit `C` outputs `0` on satisfiable `G`, provide a satisfying assignment. Verification is polynomial.

## False positive

Assume `C(G)=1` while `G` is unsatisfiable.

Evaluate `C(G_0)` and `C(G_1)`.

- If both are `0`, then the triple violates the Shannon identity at the level of circuit outputs: `C(G) != C(G_0) OR C(G_1)`. At least one of the three circuit answers is wrong, and the certificate is locally checkable.
- Otherwise choose a child with output `1` and repeat.

After at most the number of variables, either a local inconsistency was found or the process reaches a fully assigned restriction that is syntactically false while `C` still outputs `1`. The latter is also directly checkable.

## What this proves

Every erroneous SAT circuit has a polynomial-size local certificate consisting of:

1. a witnessed false negative;
2. a terminal false positive; or
3. a Shannon inconsistency triple.

## What this does not prove

The argument does not construct the first erroneous formula against an arbitrary circuit. That remains the lower-bound obligation in H060. The result only replaces a general coNP-style negative certificate with a local self-reduction certificate.

## Registry use

- observation `O040`;
- attack `A141` on H060;
- attack `A153` on H066.
