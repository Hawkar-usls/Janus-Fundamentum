# R5 E9 — Exact Levi Small-Separator Composition

Date: 2026-09-27

Status:
`JANUS_EXACT_POLYNOMIAL_SUBROUTER_THEOREM__NO_D1_PROMOTION`

Scientific firewall:

```text
THIS NOTE PROVES EXACT COMPOSITION ACROSS A LEVI EDGE CUT
AND A POLYNOMIAL ROUTER FOR FIXED-(c,B) LEAF-DECOMPOSABLE CARRIERS.

IT DOES NOT CLAIM THAT EVERY OET-IRREDUCIBLE HIGH-NULLITY CARRIER
HAS SUCH A DECOMPOSITION.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `research/R5_E9_LEVI_GENERAL_FACTOR_TWO_PERM_NORMAL_FORM_2026-09-27_v1.0.md`
- `research/R5_E9_RANK1_STITCHED_TD33_HIGH_NULLITY_2026-09-27_v1.0.md`

External anti-loop:
- Marx, Sankar, Schepper, *Degrees and Gaps: Tight Complexity Results of General Factor Problems Parameterized by Treewidth and Cutwidth*, ICALP 2021 / arXiv:2105.08980, gives an `O^*(2^k)` algorithm for General Factor from a width-`k` linear layout. The boundary-state principle below is therefore not claimed as a novel general General-Factor algorithm; JANUS needs the explicit `{1}/{0,3}` semantics, reconstruction, and carrier-specific routing certificate.

## 1. Frozen factor semantics

For the cubic bipartite Levi graph `L=(R union C,E)` of a cubic square Exact-One carrier, the exact equivalent General-Factor degree sets are

```text
K(r)={1}   for r in R,
K(c)={0,3} for c in C.
```

A valid factor is an edge set `F subseteq E` satisfying `deg_F(v) in K(v)` for all vertices. It is in bijection with an Exact-One witness: a column is selected exactly when all three of its Levi incidences belong to `F`.

## 2. Exact boundary state for one cut

Let `V=S disjoint_union T` and let

```text
D = delta(S)
```

be the set of Levi edges crossing the cut. Let `|D|=c`.

A boundary state is simply a bit vector

```text
y in {0,1}^D,
```

where `y_e=1` means crossing edge `e` is included in the factor.

For a vertex `v in S`, define

```text
b_y(v) = number of selected crossing edges in D incident with v.
```

Define the residual local degree set on the induced graph `L[S]` by

```text
K_S^y(v)
= { d >= 0 : d + b_y(v) in K(v) } intersect {0,...,deg_{L[S]}(v)}.
```

Concretely:

For a row vertex `r`:

```text
K_S^y(r) = {1-b_y(r)} if that value is a valid internal degree,
            empty otherwise.
```

For a column vertex `c`:

```text
K_S^y(c)
= { d in [0,deg_S(c)] : d+b_y(c) in {0,3} }.
```

Define `K_T^y` symmetrically.

Let `FEAS(S,y)` mean that `L[S]` has an internal edge set `F_S` whose degrees lie in `K_S^y`.

## 3. Single-cut composition theorem

### Theorem CUT-COMP-1

For every Levi cut `D=delta(S)`:

```text
L has a valid {1}/{0,3} General Factor
iff
there exists y in {0,1}^D such that
FEAS(S,y) and FEAS(T,y).
```

Moreover, if `F_S,F_T` witness those two local predicates, then a global factor is reconstructed exactly as

```text
F = F_S union F_T union {e in D : y_e=1}.
```

### Proof

Forward direction: take any global valid factor `F` and let `y` be its incidence vector on `D`. For `v in S`, split its factor degree into internal and crossing parts:

```text
deg_F(v)=deg_{F intersect E(S)}(v)+b_y(v).
```

Since `deg_F(v) in K(v)`, the internal degree belongs to `K_S^y(v)`. Thus `F intersect E(S)` witnesses `FEAS(S,y)`. The same argument applies to `T`.

Reverse direction: let `F_S,F_T` be local witnesses for the same boundary vector `y`, and add exactly the crossing edges with `y_e=1`. For every vertex the resulting total degree is by definition an element of its original target set `K(v)`. Hence the union is a valid global factor.

The constructions are inverse at the level of the cut edge choice and preserve the exact witness semantics. QED.

## 4. Complexity for a fixed cut

For fixed `c`, only `2^c` boundary vectors exist. Therefore if both sides are solvable under residual boundary degree sets in polynomial time, the cut composition adds only a constant multiplicative factor.

The boundary representation itself is `O(c)` bits. No eigenspace enumeration and no Boolean assignment enumeration is hidden in the interface.

## 5. Fixed-(c,B) leaf-peeling router

A stronger carrier-specific polynomial terminal follows for a class that can be completely peeled into constant-size Levi modules.

Fix constants `c,B`.

Call a current connected Levi graph `(c,B)`-peelable if there exists an edge cut of size at most `c` whose removal isolates a connected component containing at most `B` Levi vertices. Repeatedly remove such a component and record its attachment edges. Continue until either:

```text
(A) the remaining root has at most B vertices; or
(B) no (c,B)-peel exists while the root has more than B vertices.
```

For fixed `c`, a peel can be found in polynomial time by brute-force enumeration of all edge subsets of size at most `c`, followed by connected-component checks. Since a cubic Levi graph has `O(n)` edges, this costs `n^{O(c)}` per round and there are at most `O(n)` rounds.

### Message semantics

Every peeled module `M` has at most `B` vertices and therefore at most `3B` incident Levi edges in the original cubic graph. Child modules peeled earlier may contribute finite feasibility relations on some of those incidences. To create the message from `M` to its still-live parent, enumerate all selections of the constant number of internal/boundary incidences of `M`, retain exactly those satisfying:

```text
- all child messages,
- K(row)={1},
- K(column)={0,3},
```

and project the result to the at-most-`c` parent attachment bits.

The outgoing message is therefore a subset of `{0,1}^d`, `d<=c`, plus one backpointer per accepted state for witness reconstruction.

Because `B,c` are fixed, all local enumerations are constant-size. Combining messages over all peeled modules is polynomial in the original graph size.

### Theorem LEAF-ROUTER-1

For every fixed pair `(c,B)`, there is a deterministic exact polynomial-time algorithm with the following contract:

```text
INPUT: cubic square Levi carrier L.

If complete (c,B)-peeling reaches a root of size <=B:
    return SAT plus an Exact-One witness,
    or UNSAT,
    exactly.

If peeling stops on a root of size >B:
    return CORE together with the reduced root and all exact boundary messages.
```

`CORE` is not interpreted as evidence of UNSAT or hardness; it only means this particular polynomial subrouter is exhausted.

### Soundness and completeness

At each peel, CUT-COMP-1 proves that replacing the removed module by its exact boundary feasibility message preserves existence of a global General Factor in both directions. Induction over the peel sequence proves that the final root instance plus messages is feasible iff the original instance is feasible. Stored backpointers reconstruct the selected cut edges and internal factor of each removed module in reverse order, and the exact General-Factor/Exact-One bijection reconstructs the Boolean witness.

### Polynomial bound

For fixed `c,B`:

```text
separator discovery <= n^{O(c+1)},
message alphabet <= 2^c,
local module enumeration <= 2^{O(B)},
number of modules <= n,
reconstruction <= poly(n).
```

Thus total runtime and stored state are polynomial in `n`.

## 6. Application to the rank-1 stitched `TD(3,3)` family

Each `TD(3,3)` Levi module contains

```text
9 row vertices + 9 column vertices = 18 vertices.
```

In the stitched chain, an end module is attached to the remainder by exactly two cross incidences. After peeling it, the next module becomes an end module with the same property.

Therefore every `A_m` from the rank-1 stitched theorem is completely `(c=2,B=18)`-peelable.

### Corollary TD33-ROUTER

The entire explicit family with

```text
n=9m,
nullity_Q(A_m)=m+1=n/9+1
```

has an exact deterministic polynomial-time Exact-One decision/reconstruction algorithm by the leaf-peeling router.

So this `Theta(n)` nullity family is removed before the hard separator-resistant residual.

## 7. Stronger family-specific transfer law

The kernel theorem for one `TD(3,3)` block says any `{-1,2}` Exact-One kernel vector is constant on each of `X,Y,Z`, with exactly one of the three groups receiving value `2`. Thus each block has only three witness states:

```text
X: (a,b,c)=( 2,-1,-1)
Y: (a,b,c)=(-1, 2,-1)
Z: (a,b,c)=(-1,-1, 2).
```

The stitch equation is `b_t=a_{t+1}`. Therefore the exact state transitions are

```text
X -> Y or Z
Y -> X
Z -> Y or Z.
```

This gives a three-state linear-time DP and witness reconstruction for the family. The number of Exact-One witnesses for length `m` is

```text
F_{m+3}
```

with Fibonacci convention `F_1=F_2=1`:

```text
m=1,2,3,4,...
count=3,5,8,13,...
```

This family-specific corollary is stronger than needed for polynomiality and serves as an independent semantic check on the separator router.

## 8. Updated hard residual

The next hard carrier should not merely be OET-unrecognized and high-nullity. It must also survive the exact constant-module peeling pre-router:

```text
connected cubic linear square carrier
+ nullity_Q(A)=omega(log n)
+ no recognized OET quotient
+ not completely reducible by the admitted fixed-(c,B) separator routers
+ then attack the separator-resistant core.
```

This does not prove that all small-separator structure is exhausted. Balanced separators and decompositions with growing interface remain separate questions.

## 9. Ceiling

```text
SINGLE CUT {1}/{0,3} COMPOSITION
= PROVED EXACT

FIXED-(c,B) COMPLETE LEAF-PEEL ROUTER
= PROVED POLYNOMIAL

WITNESS RECONSTRUCTION
= PROVED

RANK1-STITCHED TD33 FAMILY
= COMPLETELY ROUTED AT (c=2,B=18)

TD33 FAMILY EXACT-ONE STATE COUNT
= F_{m+3}

ALL OET-IRREDUCIBLE HIGH-NULLITY CARRIERS
= NOT SOLVED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
