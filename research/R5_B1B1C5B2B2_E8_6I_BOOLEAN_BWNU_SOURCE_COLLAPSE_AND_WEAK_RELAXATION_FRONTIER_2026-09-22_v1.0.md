# R5 E8 6I — Boolean Bwnu Source Collapse and Weak-Relaxation Frontier

Date: 2026-09-22

Authority: `SOURCE_BOUND_SCOPE_REDUCTION__NO_D1_PROMOTION__NO_SUCCESSOR_AUTHORIZATION`

## 1. Source-exact identification of B4

Primary source:

Rustem Takhanov,
*On the induced problem for fixed-template CSPs*,
arXiv:1708.08292v3.

Open source:
https://arxiv.org/abs/1708.08292

In Appendix B.5 the source defines `B_wnu` as the family of ternary idempotent weak-near-unanimity algebras.

For the Boolean domain `D={0,1}`, the source explicitly states that `B_wnu` consists of exactly four algebras whose operations are:

```text
x AND y AND z
x OR y OR z
MAJ(x,y,z)
MINORITY(x,y,z) = x XOR y XOR z
```

Therefore the previously frozen JANUS library

```text
B4
=
{AND3, OR3, MAJ3, XOR3}
```

is exactly the source-native Boolean `B_wnu` family.

This identification is important because it removes any ambiguity about the status of B4: it is not an ad-hoc operation set.

## 2. What the source already gives for B4/Bwnu

The source constructs a weak-near-unanimity operation on the algebra-label domain `B_wnu` and concludes that:

```text
CSP(Gamma^Bwnu)
=
TRACTABLE
```

for arbitrary `Gamma`.

The same source proves Theorem 1:

```text
if B is a tractable collection
and a prototype
R -> Gamma^B
is given,

then
R -> Gamma
can be found in polynomial time.
```

The source explicitly lists `B_wnu` among its tractable algebra collections.

Thus, for Boolean 3-SAT and frozen B4:

```text
G1 ALGEBRA TRACTABILITY
=
SOURCE-BOUND PASS

G2 FIXED FAMILY DESCRIPTION / INDUCED LOCAL TABLE CONSTRUCTION
=
PASS / CONSTANT-TEMPLATE

G3 PROTOTYPE CSP SOLVE
=
SOURCE-BOUND PASS

G5 PROTOTYPE -> ORIGINAL SOLVE
=
SOURCE-BOUND PASS
```

subject to the standard fixed-template representation assumptions.

This sharply reduces the 6I frontier.

## 3. The remaining direct bridge

Takhanov's Theorem 2 states that if:

```text
B is tractable
and
Gamma -> Gamma^B,
```

then:

```text
CSP(Gamma)
<=_T^P
CSP(Gamma^B).
```

The source immediately notes that the homomorphism condition is hard to satisfy unless `B` contains constants, and that it fails for the nontrivial examples B.1-B.5, including the WNU family.

JANUS independently sealed the exact Boolean failure for the full signed 3-clause template:

`research/R5_B1B1C5B2B2_E8_6I_BOOLEAN_B4_INDUCED_ALGEBRA_KILLER_TEST_2026-09-22_v1.0.json`

The satisfiable relation

```text
NAE3
=
(x OR y OR z)
AND
(NOT x OR NOT y OR NOT z)
```

has no B4 variable-wise algebra prototype.

Therefore:

```text
DIRECT Gamma_3SAT -> Gamma_3SAT^B4
=
FALSIFIED.
```

## 4. Standard local-consistency weak relaxation also fails on NAE3

Exact checker:

`research/tools/r5_e8_6i_nae3_local_consistency_b4_barrier.py`

Receipt:

`research/R5_B1B1C5B2B2_E8_6I_NAE3_LOCAL_CONSISTENCY_B4_BARRIER_2026-09-22_v1.0.json`

For NAE3:

- every unary projection is the full Boolean domain;
- every binary projection is `{0,1}^2`;
- every assignment to at most two variables extends to an NAE3 tuple.

Hence the instance is:

```text
ARC CONSISTENT
PATH CONSISTENT
STRONG-3 CONSISTENT.
```

At the same time, exhaustive checking proves:

```text
preserving B4 label triples for NAE3
=
0.
```

Therefore standard extension-based arc/path/strong-3 consistency does not create the missing B4 prototype.

The result is scoped:

```text
STANDARD LOCAL-CONSISTENCY PRUNING
DOES NOT RESCUE B4 COVERAGE
ON THE NAE3 WITNESS.
```

It does not rule out a representation-changing preprocessing, new-variable lift, or genuinely nonlocal transformation.

## 5. Strong old positive controls: B.1-B.5

Takhanov gives several old algebra families for which the induced template is tractable for arbitrary `Gamma`:

```text
B / tournament-style conservative binary operations
B1 / tournament pairs
Bcom / commutative idempotent binary operations
Bnu / near-unanimity operations
BM / Maltsev operations
Bwnu / ternary WNU operations
```

The useful lesson is not that one of these already solves 3-SAT.

The lesson is:

```text
A TRACTABLE PROTOTYPE LAYER
CAN BE BUILT BY UNIVERSAL-ALGEBRAIC CLOSURE
WITHOUT REQUIRING THE ORIGINAL Gamma TO BE TRACTABLE.
```

The unresolved obligation is the exact coverage bridge from arbitrary satisfiable instances into that layer.

## 6. Maximal tractability-certificate control: Siggers pairs

Appendix B.6 of the same source considers `B_S`, the set of all Siggers pairs on the domain.

The source summarizes earlier lifted-language results as follows:

```text
for any input structure R,

Gamma_R tractable
iff
R -> Gamma^B_S;
```

and:

```text
CSP(Gamma)
is polynomial-time Turing reducible to
CSP(Gamma^B_S).
```

Consequently, for NP-hard `Gamma`, the source states:

```text
CSP(Gamma^B_S)
=
NP-hard.
```

This gives a source-level general control that is stronger than the toy constant-algebra control:

```text
MAXIMAL LOCAL TRACTABILITY CERTIFICATE COVERAGE
CAN PUSH HARDNESS INTO
PROTOTYPE DISCOVERY.
```

For the full Boolean 3-SAT template, taking all tractability certificates does not by itself create a polynomial discovery layer.

## 7. The 6I Goldilocks interval

We now have three exact anchors:

### Too rigid

```text
B4 = Boolean Bwnu
prototype CSP = tractable
prototype->solution = tractable
coverage = FAIL on NAE3
```

### Too expressive by direct value coding

```text
B_const
coverage = exact
prototype discovery = original SAT
```

### Maximally expressive tractability certification

```text
B_S = all Siggers pairs
local tractability coverage = maximal
prototype discovery inherits NP-hardness
for NP-hard Gamma.
```

Therefore the current missing object is not merely "a richer B".

It must be a source-bound intermediate mechanism that simultaneously provides:

```text
1. enough coverage for every satisfiable 3-CNF;
2. a polynomially solvable prototype layer;
3. tractable prototype->solution reconstruction;
4. no value-coding / witness encoding;
5. no hidden SAT/equivalence oracle;
6. polynomial preprocessing and total history.
```

## 8. Exact current theorem target

The current 6I target is refined to:

```text
R5_E8_6I_BOOLEAN_BWNU
WEAK_RELAXATION_COVERAGE_GATE_V1
```

Find an acceptable preprocessing `p`, polynomial in original input length `L`, such that for every 3-SAT instance `R`:

```text
R -> Gamma_3SAT
iff
p(R) is defined
and
p(R) -> Gamma_3SAT,
```

solutions reconstruct in polynomial time, and whenever `p(R)` is defined:

```text
Gamma_{p(R)}
->
(Gamma_3SAT^B4)_{p(R)}
```

in the source weak-relaxation sense.

The following do not qualify:

- bounded local-consistency pruning alone;
- constants/value labels that encode the satisfying assignment;
- SAT/equivalence oracles;
- exponential branch/backdoor/interface enumeration;
- semantic sweeping whose construction cost is uncharged.

## 9. Claim ceiling

```text
NEW GENERAL SAT ALGORITHM
=
NO

B4 DISCOVERY/SOLVE LAYERS
=
SOURCE-BOUND TRACTABLE

B4 DIRECT COVERAGE
=
FALSIFIED

B4 STANDARD LOCAL-CONSISTENCY RESCUE
=
FALSIFIED ON NAE3

MAXIMAL SIGGERS-CERTIFICATE DISCOVERY
=
SOURCE-BOUND NP-HARD CONTROL

CURRENT MISSING OBJECT
=
POLY WEAK-RELAXATION COVERAGE PREPROCESSING

SUCCESSOR_ALGORITHM
=
LOCKED

D1
=
EMPTY

P_VS_NP
=
OPEN
```
