# TRUMP closed/internal exact-two-factor carrier — theorem candidate

Status: `CANDIDATE_ONLY__NO_SCIENTIFIC_PROMOTION`  
Parent: `TRUMP_CURRENT_STATE_2026-09-15_v3.17`  
Frozen preregistration commit: `ea2bd90e48d725f88043a18cd91b16be3d4dfc82`  
Frozen preregistration blob: `1240d183461bfab4defe42df14ffdb2df31396da`

## 1. Scope

This candidate concerns only a unique-common-core predecessor for which every conditioned residual component is either:

1. a sealed v3.6 singleton component;
2. a sealed v3.6 two-relation component; or
3. a **closed/internal exact-two-factor component** as frozen by the preregistration.

For a component of type 3:

- every residual variable occurs in exactly two distinct component factors;
- no component residual variable belongs to the parent cut;
- after removing the unique common-core coordinates, each factor relation is exactly the Boolean Hamming-weight-two relation on its full residual scope.

Anything else returns OPEN before matching construction. In particular, a boundary-bearing two-factor component remains `OPEN_TWO_FACTOR_BOUNDARY_INTERFACE_NOT_SEALED`.

## 2. Exact incidence semantics

Let the admitted component factors be the vertices of a multigraph `G`. For every residual Boolean variable `x_e`, its two distinct factor occurrences define one multigraph edge `e`; parallel edges are distinct variables and loops are impossible by admission.

For factor/vertex `v`, its residual row relation contains exactly those assignments with

`sum_{e incident to v} x_e = 2`.

Therefore an assignment satisfies every component factor iff the selected edge set

`F = { e : x_e = 1 }`

has degree exactly two at every vertex of `G`. This is exactly a spanning 2-factor of `G`. The representation map is the identity on residual variables; there is no quotient and no loss of semantics.

## 3. Frozen Tutte f-factor gadget for f(v)=2

For each vertex `v` of degree `d(v)` construct:

- `A(v) = { a(v,e) : e incident to v }`, so `|A(v)| = d(v)`;
- `B(v) = { b(v,0), ..., b(v,d(v)-3) }`, so `|B(v)| = d(v)-2`;
- every local edge `a-b` for `a in A(v)`, `b in B(v)`.

For each original multigraph edge `e=uv`, add exactly one cross edge

`a(u,e) -- a(v,e)`.

Call the resulting simple gadget graph `H`. Distinct parallel original edges use distinct incidence vertices, so they create distinct cross edges in `H` without parallel gadget edges.

### Lemma 3.1 — 2-factor implies perfect matching

Assume `F` is a 2-factor of `G`.

For every selected edge `e=uv in F`, put the corresponding cross edge `a(u,e)a(v,e)` into a matching `M` of `H`.

At every original vertex `v`, exactly two incidence vertices of `A(v)` have now been consumed by selected cross edges. Exactly `d(v)-2` incidence vertices remain. Since `|B(v)|=d(v)-2` and `A(v) x B(v)` is complete bipartite, match the remaining incidence vertices bijectively to `B(v)` in canonical sorted order.

Every gadget vertex is covered exactly once. Thus `M` is a perfect matching of `H`.

### Lemma 3.2 — perfect matching implies 2-factor

Assume `M` is a perfect matching of `H`.

Every auxiliary vertex in `B(v)` has neighbors only in `A(v)`, so all `d(v)-2` vertices of `B(v)` consume `d(v)-2` distinct incidence vertices of `A(v)`. Hence exactly two incidence vertices of `A(v)` remain to be matched outside the local biclique.

The only nonlocal neighbor of `a(v,e)` is the corresponding incidence vertex at the other endpoint of the same original edge `e`. Therefore the two remaining incidence vertices at `v` are matched by cross edges, and those cross edges select exactly two original edges incident to `v`.

Because one cross edge simultaneously uses the two incidence copies of the same original edge, the selected original edges are globally consistent. Every original vertex has selected degree two. Hence the selected original edges form a spanning 2-factor of `G`.

### Corollary 3.3

`G` has a 2-factor iff `H` has a perfect matching.

This is an exact equivalence, not a heuristic reduction.

## 4. Static SAT certificate

A SAT certificate contains the perfect-matching edge list of `H` plus the claimed selected residual variables.

The verifier reconstructs `H` deterministically from the recognized component and checks:

1. each gadget vertex occurs in exactly one claimed matching edge;
2. every claimed matching edge exists in `H`;
3. the claimed selected residual variables are exactly the original edges whose cross gadget edges occur in the matching;
4. each original factor vertex has exactly two selected incident residual variables;
5. the corresponding conditioned factor row exists exactly.

By Lemma 3.2, a verified perfect matching yields an exact component witness. The matching solver itself is not trusted by this verifier.

## 5. Static UNSAT certificate

A claimed UNSAT certificate supplies a gadget vertex set `U`.

The verifier reconstructs `H`, deletes `U`, computes all connected components of `H-U`, and lets `q` be the number having odd cardinality. It accepts the certificate only if

`q > |U|`.

### Lemma 5.1 — Tutte obstruction soundness

Suppose a perfect matching of `H` existed. Each odd component of `H-U` cannot be perfectly matched entirely internally; at least one vertex of that component must be matched across to a vertex of `U`. Distinct odd components require distinct vertices of `U`, because a matching uses every vertex at most once. Therefore any perfect matching requires

`q <= |U|`.

Thus `q > |U|` proves that `H` has no perfect matching. By Corollary 3.3, the original component has no 2-factor.

The candidate solver's internal `NO_MATCHING` flag has zero UNSAT authority unless this static check succeeds.

## 6. Polynomial obstruction derivation candidate

Let `nu(H)` be the maximum matching cardinality returned by the self-contained deterministic Edmonds implementation.

Define

`D = { v in V(H) : nu(H-v) = nu(H) }`

and

`A = N(D) \ D`.

The candidate uses the classical Gallai-Edmonds structure theorem only to derive a proposed obstruction `U=A`: when `H` has no perfect matching, the theorem gives

`odd_components(H-A) - |A| = |V(H)| - 2*nu(H) > 0`.

Therefore `A` is a Tutte obstruction. Crucially, the implementation still performs the direct Section 5 verifier. If the derived set fails `odd_components(H-U) > |U|`, the carrier returns OPEN rather than UNSAT.

This derivation uses at most `|V(H)|+1` maximum-matching calls.

## 7. Composition with sealed v3.6

Residual components are variable-disjoint after the unique common core is fixed.

- Each residual component of size <=2 reuses only the sealed v3.6 singleton/pair carrier.
- Each admitted two-factor component is required to have empty intersection with the parent cut.

Therefore an admitted two-factor component contributes no outer boundary relation. If it is UNSAT, the whole unique-core target is UNSAT. If it is SAT, any one verified component witness may be retained independently; no Cartesian product over component witness families is required.

After every closed component is independently admitted SAT, remove the target relations exactly as in v3.6, add only the existing v3.6 boundary constraints for <=2 components, and invoke the already sealed guarded handoff.

## 8. Original-witness replay

For a successful outer guarded handoff:

1. start from the transformed assignment;
2. clear target-internal coordinates as in v3.6;
3. restore the unique common-core state;
4. restore <=2 component rows using the sealed v3.6 witness maps;
5. for every two-factor component, set each residual edge variable from the verified matching certificate and recover the exact conditioned row of every component factor;
6. call `guarded.verify_original_assignment(prep["canonical"], assignment)`.

A transformed-only witness has no SAT authority. Failure of final original replay returns OPEN.

## 9. Size bounds

Let `n=|V(G)|`, `m=|E(G)|`, and let `L` be the original explicit input size.

Because factor scopes and residual variables are explicit, `n,m = O(L)`.

The gadget has

`|V(H)| = sum_v d(v) + sum_v(d(v)-2) = 2m + (2m-2n) = 4m-2n = O(L)`.

Its edges are

`|E(H)| = m + sum_v d(v)(d(v)-2)`.

Since `sum_v d(v)=2m`,

`sum_v d(v)^2 <= (sum_v d(v))^2 = 4m^2`,

so `|E(H)| = O(L^2)`.

The frozen implementation budget is conservative:

- exact recognition and incidence indexing: `O(L^2)`;
- gadget construction: `O(L^2)`;
- one deterministic unweighted Edmonds maximum-matching call: `O(L^3)`;
- UNSAT obstruction derivation: at most `O(L)` matching calls, therefore `O(L^4)`;
- certificate verification and original replay: `O(L^2)`;
- certificate bytes: `O(L^2)` conservative.

Hence the frozen total envelope is

`T_discover + T_construct + T_solve + T_reconstruct + T_verify + certificate_bytes = O(L^4)`.

The exponent is independent of relation count.

## 10. Firewalls

This theorem candidate says nothing about:

- boundary-bearing two-factor components;
- arbitrary f-factor relations encoded by arbitrary raw CSP tables;
- arbitrary residual GT2 components;
- multiple common-core states;
- separator size four;
- general SAT or P vs NP.

`P_VS_NP = OPEN`.  
`GENERAL_SAT_IN_P = NOT_PROVED`.  
`SIZE4_BRANCHING_LICENSED = false`.
