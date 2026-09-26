# R5 E8 — Frozen Greedy Counterfamily Second-Pass Symbolic Audit

Date: 2026-09-22

Authority: `SECOND_PASS_SYMBOLIC_AUDIT__NO_D1_PROMOTION`

Audited proof:

`research/R5_B1B1C5B2B2_E8_CELL_TREE_COMPETITOR_BARRIERS_AND_FULL_ODD_PREFIX_THEOREM_2026-09-22_v1.0.md`

Audited proof head:

`6247cbec493b0a894ac0d0bcb3e345380b0d6234`

## Verdict

```text
AUDIT
=
PASS_WITH_REPAIRS

COUNTERFAMILY CONCLUSION
=
SURVIVES

GREEDY_PROJECTOR_PEAK_THEOREM_V1
=
FALSIFIED
FOR THE EXACT FROZEN SELECTOR

P_VS_NP
=
OPEN
```

## Audit A — cell-tree variant count

Claim audited:

```text
dyadic cell subtree I
has exactly
2^{|P intersect I|}
reachable structural root variants.
```

Result: PASS after making the commutative-canonicalization firewall explicit.

Reason:

- projected odd cell: exactly two distinct variants under the unresolved even anchor;
- unprojected odd cell: exactly one;
- internal variants form the Cartesian product of child variants;
- different left/right dyadic intervals contain disjoint unresolved even-selector ID sets;
- therefore a left-root ref cannot equal or complement a right-root ref;
- commutative child sorting cannot turn two different assignment pairs into the same canonical pair.

No semantic-equivalence reasoning is used.

## Audit B — weighted projected-path dominance

Claim audited:

```text
if P is proper and p in P,
some unprojected u satisfies

W_P(u) < W_P(p).
```

Result: PASS.

Induction check:

- root weight is common;
- if the projected leaf's child subtree is mixed, recurse inside it;
- if that child is fully projected, its top child-root contribution is `2^s` for subtree size `s`;
- an unprojected path in the opposite child has at most `s-1` projected leaves at the top interval and strictly smaller nested contributions;
- the height-one base is immediate.

Integer weights imply at least one unit of strict separation.

## Audit C — adjacent support union

The first proof used an unnecessarily delicate internal-path comparison.

Repair:

Choose the projected member `p` of the two distinct support cells.

Projected-path dominance gives

```text
W_P(p) >= W_P(u)+1.
```

The second distinct support cell contributes at least one additional cell-root ref outside the path of `p`.

Therefore directly:

```text
U_P(a,b)
>=
W_P(u)+2.
```

Result: PASS after simplification.

## Audit D — orphan residual structural sharing

A first draft counted two projected-odd residual OR gates containing the same orphan payload.

That was incorrect.

For the two odd support occurrences the residual clauses are canonically identical; e.g.

```text
A_{j-1}
=
B_{j-3}.
```

Structural interning therefore leaves one residual OR node, not two.

Repair:

```text
LOCAL_z
=
c_e+c_f+3

LOCAL_o
=
5

local excess
=
c_e+c_f-2.
```

The cell-tree support union supplies at least +2, hence

```text
A_z-A_o
>=
c_e+c_f.
```

The orphan savings cap remains

```text
sigma_z
<=
c_e+c_f+8,
```

while

```text
sigma_o>=8.
```

Thus

```text
E_z-E_o>=0.
```

On equality:

```text
A_z-A_o
>=
c_e+c_f
>=
2,
```

so the odd selector wins the secondary key.

Result: PASS_WITH_REPAIR.

## Audit E — even-selector local residual aliasing

Potential loophole:

An even-selector cofactor residual could have hit a two-literal residual node already produced by a previous odd projection, increasing `sigma_e` above the claimed exact value 8.

Check:

The cyclic duplicate identity is shifted by two blocks:

```text
A_i
=
B_{i-2}.
```

If `i` is even, `i-2` is also even.

Odd-only history never projected that duplicate source selector.

The original three-literal clause AIG has no payload-payload two-literal residual node.

Therefore both even-selector residual nodes are genuinely fresh and:

```text
sigma_e=8
```

is exact.

Result: PASS after explicit alias firewall.

## Audit F — competitor partition

Before all odd selectors are exhausted, every non-odd unresolved variable is exactly one of:

```text
EVEN SELECTOR

RELATED PAYLOAD
(at least one odd support still unresolved)

ORPHAN PAYLOAD
(both odd supports already projected).
```

The three barriers cover the entire competitor set.

Result: PASS.

## Audit G — m=4 scope

The strong related-payload cone-gap sufficient lemma is false at `m=4`.

This is explicitly isolated, not hidden.

The exact frozen base remains:

```text
x1 -> x3
```

before any even selector or payload.

Result: PASS_SCOPE_REPAIR.

## Audit H — asymptotic consequence

For every `m=2^r>=4`:

```text
first m/2 greedy eliminations
=
odd selectors.
```

The already-proved branch-injectivity theorem gives:

```text
LIVE_REACHABLE_NODES
>=
2^(m/2).
```

The explicit signed 3-CNF family has:

```text
L
=
Theta(m log m)
```

under ordinary bit encoding of variable identifiers.

Therefore:

```text
Peak(F_m)
>=
2^(Omega(L/log L)),
```

which is superpolynomial.

Result: PASS.

## Finite diagnostic cross-checks

These are not used as proof.

- exact frozen executor: `m=4,8,16` greedy traces agree with the theorem;
- exhaustive ordered odd-prefix states for `m=8`: no counterexample to even-selector or orphan barriers;
- 112 orphan-payload comparisons occur across those `m=8` ordered prefix states and satisfy the repaired bounds;
- sampled `m=16` odd-prefix states show no violation of the audited barriers.

## Final audited ceiling

```text
EXACT FROZEN STRUCTURAL-GREEDY SELECTOR
=
FALSIFIED AS UNIVERSAL POLY-PEAK / D1 CANDIDATE

GENERAL AIG QE
=
NOT FALSIFIED

SAT
=
NO LOWER BOUND CLAIM

P_VS_NP
=
OPEN

SUCCESSOR
=
LOCKED UNTIL POSTMORTEM + ANTI-DUPLICATION REVIEW
```
