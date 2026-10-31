# R5 E9 — Rooted Dual-Fano / E10 Cross-Route Reconciliation

Date: 2026-09-28

Status: `JANUS_EXACT_CROSS_ROUTE_RECONCILIATION__ROOTED_DUAL_FANO_ALONE_NOT_CANONICAL_HARD_CORE__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT DECIDER.
IT PREVENTS A REGRESSION IN WHICH THE NEW ROOTED F7/F7* LANGUAGE
IS TREATED AS THE WHOLE HARD CORE WHILE OLDER E9/E10 POLYNOMIAL
TERMINALS ARE FORGOTTEN.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. New single-odd terminal and old E10 must be intersected

For a cubic square Exact-One source with binary incidence matrix `A`, put

```text
b = 1,
M = M_F2([A|b]),
e_b = distinguished syndrome element.
```

The current source stack proves

```text
Exact-One SAT
iff
mu(A)=n/3,

mu(A)=minimum weight circuit through e_b.
```

Truemper's single-odd theorem gives a deterministic polynomial terminal when at least one of

```text
NO_ROOTED_F7_THROUGH_e_b
NO_ROOTED_F7STAR_THROUGH_e_b
```

holds.  Therefore a survivor of that terminal must contain both rooted obstruction types.

However the repository already had the stronger, orthogonal E10/E9 stack:

- no-S8 binary matroids are polynomial for the rooted shortest-circuit objective;
- explicit low-rational-nullity source instances are polynomial;
- commuting / abelian two-permutation instances are polynomial;
- fixed-factorization Z3 phase-PASS instances are polynomial;
- balanced/perfect-conflict/separator and other certified terminals remain valid.

Hence

```text
ROOTED F7 + ROOTED F7*
```

is only one necessary survivor condition.  It is not by itself the canonical hard core.

## 2. Exact cross-route killer control: the old n=15 E10 leaf

Use the explicit cubic parent from the E10A q_graph falsifier:

```text
n = 15,
A = I + P + P^4
```

with `P` the cyclic permutation and append `b=1`.

The old E10A artifacts already prove that the augmented matroid is:

```text
3-connected,
no nontrivial exact 3-separation,
contains S8,
q_graph >= 4,
not in the graphic/even-cycle/graft/even-cut terminals used there.
```

The companion checker now verifies that it also survives the newer rooted single-odd terminal.

### Rooted F7* certificate

Keep original columns

```text
{0,1,2,3,4,5}
```

plus `e_b`, contract

```text
{6,7,8,11,12,13,14}
```

and delete

```text
{9,10}.
```

The seven-element minor has rank four, cycle-space dimension three, and its seven nonzero cycles all have weight four.  Hence it is `F7*`, retaining `e_b`.

### Rooted F7 certificate

Keep original columns

```text
{0,1,2,4,5,8}
```

plus `e_b`, contract

```text
{3,6,7,9,10,11,12,13}
```

and delete

```text
{14}.
```

The seven-element minor is simple of rank three, hence it is `F7`, retaining `e_b`.

Therefore

```text
ROOTED F7 THROUGH e_b      = YES
ROOTED F7* THROUGH e_b     = YES
S8 MINOR                   = YES
q_graph                    >= 4
```

all hold simultaneously on this literal cubic source.

## 3. But this is still not a hard source instance

The same matrix is

```text
A = I + P + Q,
Q=P^4.
```

Thus `P` and `Q` commute.  More directly, exact rational elimination gives

```text
rank_Q(A)=15,
nullity_Q(A)=0,
det(A)=144.
```

The already proved full-rank / rational-kernel terminal therefore returns `UNSAT` in polynomial time.  Exhaustive finite replay agrees: this source has zero Exact-One witnesses.

So the combination

```text
S8 + high q_graph + rooted F7 + rooted F7*
```

still does not isolate semantic hardness.

## 4. Correct intersection residual

A source instance can be treated as genuinely unresolved only after applying all already proved exact terminals.  In particular, a candidate residual must survive, where applicable:

```text
rooted single-odd F7/F7* terminals,
no-S8 shortest-circuit terminal,
rational-kernel low-nullity/full-rank terminal,
commuting / abelian two-permutation terminal,
Z3 phase terminal,
small-separator exact composition,
balanced/perfect-conflict and other certified P-islands.
```

The surviving semantic direction is therefore not a new one-minor gate.  It remains the globally coupled source semantics already isolated by the later E9 stack:

```text
NONCOMMUTING
+
PHASE-INCONSISTENT
+
NO LOW-NULLITY EXIT
+
NO KNOWN MATROID / GRAPH / SEPARATOR TERMINAL
+
GLOBAL EXACT-ONE / CROSS-LAYER COUPLING.
```

Equivalently, the new matroid terminals are preprocessors inside the universal solver, not replacements for the global-pivot obligation.

## 5. Anti-loop rule

Do not again promote any one of

```text
rooted F7/F7*,
S8 presence,
q_graph,
raw nullity,
odd-hole presence
```

as the canonical hard core without intersecting the complete terminal stack.

The next admissible mathematical theorem must either:

1. give a deterministic polynomial contraction on the full intersection residual; or
2. add a new polynomial terminal and explicitly reconcile it with all older routes; or
3. provide the end-to-end universal solver contract.

## 6. Ceiling

```text
OLD n=15 E10 LEAF SURVIVES ROOTED F7/F7* TEST
= PROVED BY EXPLICIT MINORS

OLD n=15 E10 LEAF IS STILL POLYNOMIAL
= YES, rank_Q(A)=15 / commuting island

ROOTED DUAL-FANO ALONE AS CANONICAL HARD CORE
= REJECTED

CANONICAL OBLIGATION
= INTERSECTION-RESIDUAL GLOBAL CONTRACTION / GLOBAL PIVOT

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```