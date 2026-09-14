# C023R algebraic cache-fiber lemmas v1.0

Authority: `DIAGNOSTIC_MATHEMATICAL_NOTE__NO_SCIENTIFIC_PROMOTION`

This note does not infer asymptotics from finite runs. It derives exact identities from the frozen MAJ3-lifted Tseitin encoding and exact canonical residual semantics.

## Lemma 1 — truth-table CNF commutes with restriction

Let `C(P)` be `exact_relation_cnf(X,P)`: one blocking clause for every falsifying total assignment of relation `P`.
For any partial assignment `alpha` on `A subset X`, simplifying `C(P)` by `alpha` yields exactly the blocking-clause CNF of the restricted relation `P|alpha` on `X\A`, after canonical duplicate removal.

Proof. A blocking clause from a full assignment inconsistent with `alpha` contains an `alpha`-satisfied literal and disappears. A blocking clause from the unique extension `alpha union y` of a remaining assignment `y` survives and loses precisely the literals fixed by `alpha`, becoming the blocker of `y`. Thus falsifying remaining assignments are in bijection with surviving reduced clauses. QED.

Repeated unit propagation is therefore repeated exact restriction. The Policy-0A cache key, formed after exhaustive pre-unit propagation and before local Resolution, is an exact restricted-CNF object; local Resolution does not define cache equality.

## Lemma 2 — complete MAJ3 partial-restriction table

For `M(a,b,c)=MAJ3(a,b,c)` and any choice of coordinates:

- no assigned coordinates: `M`;
- one assigned coordinate `0`: `AND` of the other two;
- one assigned coordinate `1`: `OR` of the other two;
- two assigned coordinates `00`: constant `0`;
- two assigned coordinates `11`: constant `1`;
- two assigned coordinates `01` or `10`: the remaining coordinate;
- three assigned coordinates: the corresponding constant MAJ3 output.

This follows directly from the Boolean definition `sum(bits)>=2`; coordinate symmetry is exact.
## Lemma 3 — local MAJ3 information loss is exact

Fix which two coordinates of a block are assigned and which coordinate remains live. The assignments `01` and `10` to the fixed coordinates produce the same restricted function: the remaining literal itself. Hence the exact restricted CNF cannot distinguish those two histories.

If all three coordinates are assigned, each output value of MAJ3 has exactly four preimages. Therefore a fully eliminated block contributes four internal assignments for each fixed effective edge output at the semantic restriction level.

These are not heuristic collisions; they are exact equalities of restricted Boolean functions.

## Lemma 4 — eliminated lifted edges are remembered only through vertex syndrome

For a Tseitin vertex relation

`XOR_{e incident v} MAJ3(block_e) = charge(v)`,

let `H` be a set of edge blocks that have been completely eliminated and let `z_e` be the fixed MAJ3 output of each eliminated block. The remaining vertex relation has charge

`charge'(v) = charge(v) XOR XOR_{e in H incident v} z_e`.

Writing `B_H` for the mod-2 vertex-edge incidence matrix of `H`, the residual charge vector is

`charge' = charge XOR B_H z`.

Thus two eliminated-edge output assignments `z,z'` with `B_H z = B_H z'` induce the same remaining parity relations, provided the restrictions of all non-eliminated blocks are held fixed.

## Lemma 5 — cycle-space multiplicity

For an undirected graph `H`,

`dim ker(B_H) = |E(H)| - |V(H)| + c(H)`,

where `c(H)` is the number of connected components including only vertices incident to `H` in the standard cycle-rank convention. Therefore every attainable syndrome has exactly

`2^{beta(H)}`

edge-output preimages, where `beta(H)` is the cycle rank.
## Corollary — semantic preimage capacity can be exponential

Fix all restrictions outside a fully eliminated edge set `H`. Among complete assignments to the three internal variables of every block in `H`, a fixed residual vertex-syndrome has

`4^{|E(H)|} * 2^{beta(H)}`

semantic preimages: four MAJ3 assignments per fixed edge output, multiplied by the `2^{beta(H)}` output vectors in one incidence-syndrome coset.

This is a statement about the restriction map, not about contexts actually visited by frozen Policy-0A. Deterministic search may realize only a subset because MAJ3 can become stifled before all three coordinates are branched.

## Consequence for the C023R route

A subexponential cache-fiber theorem cannot follow from generic residual injectivity or from live-variable counting alone. The frozen encoding has an exact linear-algebraic mechanism that can erase linearly many history bits.

Therefore the remaining theorem obligation is execution-specific:

> Prove that the deterministic Policy-0A branch/UP/local-Resolution dynamics can reach at most `2^{o(n)}` contexts in any one semantic residual coset on the frozen infinite MAJ3-lifted expander-Tseitin family.

Equivalently, one must prove a bound on *reachable representatives per MAJ3-stifling/cycle-space coset*, not merely characterize the residual itself.

If such a reachability theorem fails, the cache-fiber transfer from C022 fails even though C022 remains valid for no-cache Policy-0T.

## Finite revealed result already obtained

The frozen C023R runner verified exactly on MAJ3-K4:

- cached unique states: `2427`;
- no-cache expanded states: `11620`;
- `sum_R m(R) = 11620` exactly;
- `m_max = 128`;
- weighted state-local work from DAG multiplicities equals frozen no-cache Policy-0T weighted work exactly.

These values are finite diagnostics only. They are not used to choose an asymptotic law.

## Claim boundary

`SEMANTIC_PREIMAGE_CAPACITY != EXECUTION_FIBER_LOWER_BOUND`.
`FINITE_K4_MULTIPLICITY != ASYMPTOTIC_MULTIPLICITY`.
`C023R_DIAGNOSTIC != POLICY0A_LOWER_BOUND_THEOREM`.
`POLICY0A_LOWER_BOUND != P != NP`.
