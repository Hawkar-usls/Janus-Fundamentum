# R5 E63 — E12 Non-Affine C5 Packing / Raw-Parameter Firewall

Date: 2026-10-03

Status:
`E12_HAS_LINEAR_DISJOINT_NONAFFINE_STRONG_C5_PACKING__RAW_NULLITY_AND_BALANCED_MODULATOR_ARE_LINEAR__LOCAL_QUOTIENT_RETURNS_RXC3`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

IT STRESS-TESTS THE POST-E62 HOPE THAT DEGREE 3 + LINEARITY MIGHT FORCE THE
NON-AFFINE STRONG-ODD-CYCLE INTERFACES TO OVERLAP SO HEAVILY THAT THEIR
GLOBAL FREEDOM BECOMES SMALL.

THAT HOPE IS FALSE IN RAW FORM ON THE FROZEN E12 HARDNESS BRIDGE.

ONE 17-COLUMN E12 GADGET CONTAINS EXACTLY 12 LOCAL STRONG 5-CYCLES.
AFTER THE REAL PORT IDENTIFICATION INSIDE THE GADGET, EVERY ONE OF THESE
C5'S HAS FOUR DISTINCT EXTERNAL PORTS AND A FIVE-STATE NON-AFFINE RELATION.

MOREOVER, FROM EACH OF THE q GADGETS ONE CAN CHOOSE A CANONICAL STRONG C5
SO THAT THE q CHOSEN CYCLES ARE PAIRWISE INCIDENCE-DISJOINT.

THEREFORE EVERY EDGE MODULATOR WHOSE DELETION MAKES THE DUAL HYPERGRAPH
BALANCED HAS SIZE

    t >= q = n/17.

SO THE RAW E62 SOLVER 2^t * poly(n) IS EXPONENTIAL ON THE E12 REPRESENTATION.

R5 E17 ALREADY GIVES THE PARALLEL KERNEL FACT:

    dim_R ker(B) = 2q + 2 dim_R ker(R),

SO THE RAW E61 PARAMETER ALSO HAS THE LINEAR TERM

    d >= 2q = 2n/17.

THESE LARGE RAW PARAMETERS ARE LOCAL-GADGET ARTIFACTS, NOT A NEW PROOF OF
GLOBAL HARDNESS: R5 E53 COMPLETELY ELIMINATES EACH 17-COLUMN GADGET AND
RECOVERS TWO COPIES OF THE ORIGINAL RXC3 QUOTIENT.

THE CORRECT LESSON IS THAT RAW NULLITY, RAW ODD-CYCLE COUNT, RAW ODD-CYCLE
PACKING, AND RAW BALANCED-MODULATOR SIZE ARE ALL VULNERABLE TO BOUNDED-MODULE
INFLATION.  A UNIVERSAL SOLVER MUST FIRST QUOTIENT EXACT LOCAL MODULES AND
THEN ATTACK THE EFFECTIVE GLOBAL QUOTIENT.

P_VS_NP = OPEN.
```

## 1. Question attacked

R5 E62 rewrote Exact-One as perfect matching in a 3-uniform, 3-regular, linear
hypergraph and identified strong odd cycles as the obstruction to the balanced
integrality region.  It also gave the exact cycle interface relation `R_l` and
showed:

```text
strong C3 -> affine XOR interface,
strong C5 -> first generic non-affine interface.
```

A natural next hope was:

```text
perhaps degree 3 + linearity forces the non-affine C5,C7,... interfaces to
strongly overlap, leaving only a small number of genuine global degrees of
freedom.
```

E63 tests that hope directly on the frozen NP-hard E12 reduction family.

## 2. A canonical strong C5 inside every E12 gadget

Recall one unprimed E12 gadget for a source triple

```text
C_j={x_1,x_2,x_3}.
```

Among its target rows are

```text
L_1={x_1,z_1,z_4},
L_4={z_1,z_2,z_3},
D_1={z_2,z_6,t_1},
D_2={z_3,z_4,t_2},
D_7={t_1,t_2,t_3}.
```

These five row-vertices and the five selectable hyperedges

```text
z_1,z_2,t_1,t_2,z_4
```

form the induced Levi cycle

```text
L_1-z_1-L_4-z_2-D_1-t_1-D_7-t_2-D_2-z_4-L_1.
```

Equivalently, in the dual exact-cover hypergraph this is a strong 5-cycle.

The cycle uses only gadget-internal hyperedges.  Therefore the same template
exists independently in every gadget, regardless of how the global boundary
variables are wired by the RXC3 source.

## 3. The real E12 C5 interface remains non-affine

At the five cycle vertices, the unique third incident hyperedges are

```text
L_1 : x_1,
L_4 : z_3,
D_1 : z_6,
D_7 : t_3,
D_2 : z_3.
```

So the generic five-port C5 interface of E62 has a real E12 identification:

```text
port 1 = port 4 = z_3.
```

Let the four distinct external bits be ordered as

```text
(x_1,z_3,z_6,t_3).
```

Eliminating the five cycle-edge bits from the five Exact-One equations gives
exactly the relation

```text
boxed:
P5 = {
  0001,
  0010,
  1000,
  1100,
  1111
}.
```

This relation is not affine over `F_2`.  For example,

```text
0001,
0010,
1000
```

are all allowed, while their ternary XOR

```text
1011
```

is not allowed.  Every affine relation is closed under ternary XOR.

Thus the repeated E12 port does **not** collapse this strong C5 to the affine
triangle situation from E62.

## 4. Exact local count: 12 strong C5 per gadget

The companion checker constructs one E12 gadget with six distinct boundary
ports and enumerates induced length-10 cycles in its Levi graph.

It finds exactly

```text
12
```

such cycles.

For every one of the 12 cycles:

```text
number of distinct external ports = 4,
number of allowed interface states = 5,
interface affine over F_2          = false.
```

So one fixed E12 gadget already contains a dense local network of non-affine
strong-C5 interfaces.

This count is local and source-independent.  Hence an E12 target with `q`
gadgets contains at least

```text
12q
```

local strong 5-cycles.

The 12 cycles inside one gadget overlap heavily.  The next section shows that
this does not rescue the hoped-for global small-packing argument.

## 5. Linear pairwise-disjoint C5 packing

Choose in every gadget exactly the canonical cycle from Section 2.

For distinct gadgets:

```text
* the five cycle row-vertices are distinct;
* the five cycle hyperedges are all internal and distinct;
* no boundary hyperedge belongs to the cycle itself.
```

Therefore these `q` canonical cycles are pairwise incidence-disjoint.

Let `nu_5` denote the maximum number of pairwise hyperedge-disjoint strong
5-cycles.  Then every E12 target satisfies

```text
boxed:
nu_5 >= q = n/17.
```

So degree 3 and linearity do **not** imply a logarithmic or constant packing of
non-affine strong odd cycles.

## 6. Consequence for the E62 balanced-edge parameter

R5 E62 uses a set `F` of hyperedges whose deletion makes the hypergraph
balanced.  Such a set must hit every strong odd cycle.

The `q` cycles from Section 5 are pairwise hyperedge-disjoint.  Hence any such
edge modulator must choose at least one hyperedge from each one:

```text
boxed:
t_balanced >= q = n/17.
```

Therefore the exact E62 solver

```text
2^t * poly(n)
```

cannot become a universal polynomial algorithm merely from a theorem of the
form

```text
all square-cubic-linear carriers have t=O(log n).
```

The E12 hardness bridge explicitly violates such a raw bound.

Important qualification: this does **not** mean the local C5 packing itself is
irreducible global hardness.  Sections 8-9 explain why it is local module debt.

## 7. Parallel consequence for the E61 raw-nullity parameter

R5 E17 already proved the exact rational/real kernel formula for the complete
E12 reduction:

```text
boxed:
nullity_R(B) = 2q + 2 nullity_R(R),
```

where

```text
B = E12 target incidence matrix,
R = source RXC3 incidence matrix.
```

The `2q` term is the direct sum of two zero-boundary local gauge modes per
gadget.

Thus for every E12 target

```text
boxed:
d_raw = dim_R ker(B) >= 2q = 2n/17.
```

So the raw E61 solver

```text
2^d * poly(n)
```

also cannot be made universally polynomial by a raw nullity bound on the E12
representation.

The companion E63 checker replays this on the full-rank cyclic source fixtures

```text
q=6,9,12,
C_i={i,i+1,i+3} mod q,
```

where the source nullity is zero and therefore

```text
q=6  : n=102, d=12,
q=9  : n=153, d=18,
q=12 : n=204, d=24.
```

These are exactly the linear local-gauge terms `d=2q`.

## 8. Why this does not contradict local compression

The raw parameters `d` and `t` are large because the E12 representation contains
bounded gadgets with substantial local structure.

R5 E53 already performed **complete Boolean elimination** of one 17-column E12
gadget.  It found exactly eight valid local states, whose six boundary ports
collapse to just two bits

```text
a_j,
b_j.
```

All four pairs

```text
(a_j,b_j) in {0,1}^2
```

are locally realizable.

After eliminating every gadget interior, the entire `17q`-variable target
becomes exactly

```text
R a = 1,
R b = 1,
```

that is, two independent copies of the original RXC3 source.

Therefore the linear raw C5 packing and the linear raw nullity are **compressible
local representation overhead**.

But the compression only gives

```text
17q target variables -> q source variables,
```

and the quotient is the original NP-hard global language.

This is the essential E63 firewall:

```text
large local obstruction count != irreducible global dimension,
small bounded-module quotient != polynomial solution.
```

## 9. Connection with the E61/E62 parameterized solvers

We now have two exact parameterized algorithms:

```text
E61: 2^d * poly(n),
     d = raw real nullity;

E62: 2^t * poly(n),
     t = raw balanced edge-modulator size.
```

E63 shows that on the E12 hardness representation both raw parameters are
provably linear:

```text
d >= 2n/17,
t >= n/17.
```

So neither parameter, used before local quotienting, is the missing universal
polynomial invariant.

This is completely consistent with R5 E17 and E53:

```text
raw local gauge / cycles
        |
        v
exact bounded-module elimination
        |
        v
global RXC3 quotient
        |
        v
hard Boolean intersection remains.
```

## 10. External anti-loop anchor

The broader literature points in the same direction.  Denman and Foster show
that positive one-in-three SAT is polynomial when each variable occurs at most
two times but becomes NP-complete for every occurrence bound `k>2`:

* Richard T. Denman, Stephen Foster,
  "Using clausal graphs to determine the computational complexity of
  k-bounded positive one-in-three SAT",
  Discrete Applied Mathematics 157(7), 1655-1659 (2009),
  DOI 10.1016/j.dam.2008.09.011.

The E12 bridge is more structured than that general bounded-occurrence result,
but the literature reinforces the same warning: degree three is exactly where
bounded-occurrence Exact-One can already support NP-hard global interaction.

For perfect matching, Han et al. also explicitly use NP-completeness of perfect
matching in linear 3-uniform hypergraphs (`PM_lin(3)`):

* Han et al., "The complexity of almost perfect matchings and other packing
  problems in uniform hypergraphs with high codegree",
  European Journal of Combinatorics 34(3), 632-646 (2013),
  DOI 10.1016/j.ejc.2011.12.009.

These are anti-loop anchors, not substitutes for the stronger self-contained
E12 reduction already frozen in Fundamentum.

## 11. New universal frontier

The post-E62 question was

```text
Can the raw network of R_5,R_7,... interfaces be compressed polynomially
because degree 3 and linearity force strong overlap?
```

E63 answers:

```text
not from raw overlap/packing alone.
```

The E12 hard family already contains a linear pairwise-disjoint non-affine C5
packing.

At the same time, blindly branching on those cycles is also the wrong response,
because complete local elimination removes them and simply exposes RXC3.

Therefore the next useful object must be **post-quotient / effective** rather
than raw.  A candidate research program is:

```text
1. recognize bounded exact modules;
2. compute their complete Boolean boundary relations;
3. quotient all purely local kernel/cycle debt;
4. measure obstruction dimension only on the reduced interaction system;
5. attack the surviving singular RXC3-like quotient globally.
```

The next high-value theorem must therefore act on the quotient itself, not on the
internal E12 representation.

A concrete target for E64 is:

```text
Given a square 3-regular Exact-One quotient R a=1,
can its affine parity coset / full-support ternary form / strong-odd-cycle
structure be compressed by a global invariant that is unchanged by bounded
module substitution?
```

Until that is proved:

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e63_e12_nonaffine_c5_packing_raw_parameter_firewall.py
```
