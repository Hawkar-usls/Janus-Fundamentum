# C043 — Bounded Live Signed Affine-Intersection Support

```text
C043 = ARCHITECTURE_CONTRACT_ADMITTED
       / FULL_IMPLEMENTATION_CANDIDATE
P_VS_NP=OPEN
```

C043 now accepts a CNF plus affine equations, inherits the complete C042 provenance-carrying basis artifact, and forbids a free coordinate table.

The producer is split into:

```text
experiments/direct/janus_c043_crossing_core.py
experiments/direct/janus_c043_crossing_solver.py
```

The independent verifier is:

```text
experiments/direct/janus_c043_crossing_verifier.py
```

It does not import or call `solve_crossing`.

## Exact invariant

For deterministic factor order,

```text
1_(union_{i <= t} U_i) = sum_S c_t(S) 1_S
c_t = c_(t-1) + e_(U_t) - T_(U_t)c_(t-1)
T_U(S) = S intersect U.
```

The controlling parameter is

```text
K_t = |supp(c_t)|
K   = max_t K_t.
```

The factor order is descending affine-system rank, then canonical RREF, then canonical clause identifier. Changed order is rejected.

Every transition records each canonical intersection, signed delta, coefficient merge, zero cancellation, outgoing terms, live support, temporary working support and coefficient bit volume. Algebraic induction verifies the union indicator globally without enumerating `2^d` points.

## Fixed capability

For encoded input length `L`:

```text
K <= 4(L+1)^2
work <= 128(L+1)^7
certificate bytes <= 64(L+1)^6
coefficient bit volume <= 16(L+1)^3
```

Optional operational caps may only reduce these fixed bounds.

Strict terminals:

```text
OPEN_INTERSECTION_CLOSURE
OPEN_WORK_BUDGET
OPEN_CERTIFICATE_VOLUME
```

## Independent replay

The verifier independently checks:

- input and capability binding;
- C042 RREF provenance, particular solution, nullspace basis and coordinate forms;
- clause translation and factor provenance;
- deterministic factor order;
- every signed transition and cancellation;
- maximum live and working support;
- coefficient bit volume;
- exact root signed count;
- both conditional-count branches at every coordinate;
- lifted SAT witness or exact signed UNSAT cover;
- the first support-overflow transition.

## Frozen audit

```bash
python experiments/direct/janus_c043_bounded_affine_intersection_closure.py --self-test
```

```text
120 random dimensions <= 7
120 exact terminals
0 SAT/UNSAT mismatches
0 witness failures
0 independent verification failures

64-dimensional crossing SAT, K=3
64-dimensional crossing UNSAT, K=4
C042 basis-inheritance control

small final / large intermediate:
32 live terms -> final support 1
support cap 8 -> OPEN_INTERSECTION_CLOSURE at attempted K=9

coefficient bit-volume pressure -> OPEN_WORK_BUDGET
C023/C041 controls n=18,24,30 -> OPEN_INTERSECTION_CLOSURE

tampered basis -> REJECTED
changed factor order -> REJECTED
corrupt cancellation trace -> REJECTED
corrupt SAT witness -> REJECTED
corrupt signed UNSAT cover -> REJECTED
```

Frozen digest:

```text
a98693890ce3cda82d0a2d0860092f2f5b09419b7f548cee110632689681abe2
```

## Admission boundary

The two principal implementation obligations are now closed. Promotion to `FULLY_ADMITTED` is still manual and requires exact-head CI plus review of refusal-terminal capability replay. No automatic merge or status promotion is permitted.

## C044 boundary

C044 remains specification-only and starts only after a genuine C043 `OPEN_INTERSECTION_CLOSURE`.

```text
POLYNOMIAL_LOCALIZATION_OF_SUPERPOLYNOMIAL_GLOBAL_INTERSECTION_SUPPORT
OPEN_LOCAL_SUPPORT
```

C043 covers only global bounded maximum live signed support. Local-vtree completeness, arbitrary CNF, unrestricted Horn-affine composition and P versus NP remain open.
