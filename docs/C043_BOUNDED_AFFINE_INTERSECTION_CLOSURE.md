# C043 — Bounded Live Signed Affine-Intersection Support

```text
C043 = ARCHITECTURE_CONTRACT_ADMITTED
       / FULL_IMPLEMENTATION_CANDIDATE
P_VS_NP=OPEN
```

## Exact input contract

C043 receives a CNF formula together with affine equations over the original variables. It no longer receives a free coordinate map.

The shared C042 affine core constructs and records

```text
x = p + B lambda
```

by provenance-carrying Gaussian elimination. The certificate binds the complete basis artifact by SHA-256. The independent C043 verifier recomputes canonical RREF, checks every provenance XOR, checks the particular solution, nullspace vectors, free-coordinate independence and every original-variable coordinate form.

Only after this replay are clause-falsifying affine subspaces constructed.

## Primary parameter

Process the nonempty forbidden subspaces in one deterministic order and maintain

```text
1_(union_{i <= t} U_i) = sum_S c_t(S) 1_S.
```

The controlling parameter is

```text
K_t = |supp(c_t)|
K   = max_t K_t.
```

`K` is maximum live signed support, not the number of crossing pairs, not final support only, not codimension and not a supplied intersection poset.

The deterministic order places higher-rank forbidden systems first and then orders by canonical RREF and clause identifier. A changed order is rejected by the verifier.

## Signed transition

Adding factor `U_t` uses

```text
c_t = c_(t-1) + e_(U_t) - T_(U_t)c_(t-1)
T_U(S) = S intersect U.
```

For every step the proof object records:

- the exact incoming support size;
- every independently reproducible affine intersection;
- every signed delta coefficient;
- every coefficient merge;
- zero-coefficient deletion;
- outgoing canonical terms;
- `K_t` and temporary working support;
- total coefficient bit volume.

The identity follows by induction from

```text
1_(A union U) = 1_A + 1_U - 1_A 1_U.
```

No enumeration of `2^d` coordinate points is required.

## Fixed capability

For explicit encoded length `L`, the implementation fixes:

```text
K <= 4(L+1)^2
work <= 128(L+1)^7
certificate bytes <= 64(L+1)^6
coefficient bit volume <= 16(L+1)^3
```

Optional operational caps may only reduce these limits. All exponents and multipliers are fixed in the implementation and rebound by the verifier.

Exact refusal terminals are:

```text
OPEN_INTERSECTION_CLOSURE
OPEN_WORK_BUDGET
OPEN_CERTIFICATE_VOLUME
```

A support overflow is emitted at the first step where `K_t` exceeds the effective support limit. Later cancellation cannot rescue that run.

## Independent verifier

The verifier is a separate module:

```text
experiments/direct/janus_c043_crossing_verifier.py
```

It does not import or call `solve_crossing`.

It independently checks:

1. input and capability binding;
2. the complete C042 affine basis artifact;
3. clause translation and factor RREF provenance;
4. deterministic factor order;
5. every signed transition and cancellation;
6. maximum live and working support;
7. coefficient bit volume;
8. exact signed root count;
9. conditional signed counts for both children of every prefix;
10. the coordinate witness and lifted original assignment;
11. the exact signed UNSAT cover.

For `OPEN_INTERSECTION_CLOSURE`, it independently rebuilds the first overflowing transition and verifies the attempted support against the fixed capability.

## Exact decision

For final coefficients `c(S)`, the union cardinality is

```text
|union_i U_i| = sum_S c(S) 2^dim(S).
```

Equality with `2^d` gives an exact signed UNSAT cover. Otherwise conditional signed counting fixes one coordinate at a time. At each prefix cell `P`:

```text
|P intersect union_i U_i|
  = sum_S c(S) |P intersect S|.
```

A child whose signed covered count is smaller than its cell size contains an uncovered coordinate. The final coordinate lifts through the verified C042 basis to an original SAT witness.

## Frozen hardening audit

```bash
python experiments/direct/janus_c043_bounded_affine_intersection_closure.py --self-test
```

The deterministic suite includes:

```text
120 random CNFs on dimensions <= 7
120 exact terminals
0 SAT/UNSAT mismatches
0 witness failures
0 independent verification failures

64-dimensional crossing SAT with K=3
64-dimensional crossing UNSAT signed cover with K=4
C042 affine-basis inheritance control

32 live singleton terms followed by a universal blocker
-> final support 1
-> maximum live support 32
-> tight capability returns OPEN_INTERSECTION_CLOSURE at K=9

coefficient bit-volume pressure -> OPEN_WORK_BUDGET
C023/C041 hard images at n=18,24,30 -> OPEN_INTERSECTION_CLOSURE

tampered basis artifact -> REJECTED
changed factor order -> REJECTED
corrupt cancellation trace -> REJECTED
corrupt SAT witness -> REJECTED
corrupt signed UNSAT cover -> REJECTED
```

Frozen audit digest:

```text
a98693890ce3cda82d0a2d0860092f2f5b09419b7f548cee110632689681abe2
```

## C044 boundary

C043 is a global theorem. It does not localize a superpolynomial global signed support.

C044 is reserved for:

```text
POLYNOMIAL_LOCALIZATION_OF_SUPERPOLYNOMIAL_GLOBAL_INTERSECTION_SUPPORT
```

A C044 message may contain a boundary affine relation, local signed family, coefficients, count semantics and replay trace. Every join and projection must charge maximum local intermediate support. Overflow returns `OPEN_LOCAL_SUPPORT`.

C044 remains specification-only until C043 receives final review admission.

## Claim boundary

C043 covers only instances whose global maximum live signed support, coefficient volume, construction work and proof volume fit one fixed polynomial capability. Arbitrary CNF, unrestricted Horn-affine composition, local-vtree completeness and P versus NP remain open.
