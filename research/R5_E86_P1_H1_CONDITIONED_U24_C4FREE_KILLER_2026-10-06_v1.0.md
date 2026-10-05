# R5 E86 — p=1,h=1 Conditioned-U2,4 C4-Free Killer

Date: 2026-10-06

Status:
`P1_H1_CONDITIONED_U24_EXCLUDED_FOR_T_LE_2__FIRST_OPEN_SIZE_T3`

Scientific ceiling:

```text
E86 DOES NOT EXCLUDE ALL CONDITIONED U2,4 MINORS.

IT CLOSES THE SMALLEST NEW E85 ZERO-HOLE ORIENTATION
    p=1, h=1
FOR THE FIRST TWO ARITHMETICALLY POSSIBLE SIZES:
    t=1 -> 4 checks / 3 variables
    t=2 -> 7 checks / 6 variables.

THE FIRST OPEN SIZE IN THIS LANE IS
    t=3 -> 10 checks / 9 variables.

OTHER E85 ORIENTATIONS p=0,2,3,4 ALSO REMAIN OPEN BEYOND THE ALREADY-CLOSED
DIRECT E84 LANE.

P_VS_NP = OPEN.
```

## 1. E85 normal form specialized to p=1,h=1

E85 proved that every hypothetical (U_{2,4})-minor can be converted into a
four-free-port conditioned Tanner relation.  Let

[
p=1,qquad q=3,qquad h=1.
]

The universal E85 identity

[
h=3(a-b)+2p-4
]

gives

[
1=3(a-b)-2,
]

hence

[
oxed{a=b+1.}
]

The selected-variable count identity

[
|Y_F|=rac{a+p-2}{3}
]

gives

[
aequiv1pmod3.
]

Therefore for some integer (tge1),

[
oxed{
a=3t+1,qquad b=3t,qquad |Y_F|=t.
}
]

The conditioned four-port family is (U_{2,4}) twisted by its single
variable-side survivor coordinate. In the frozen ordering with three check-side
bits first and the variable-side bit last:

[
oxed{
mathcal F_{p=1}
=
{0001,0010,0100,1011,1101,1110}
}
]

or, as integer masks,

[
{1,2,4,11,13,14}.
]

When the variable boundary bit is 0, exactly one of the three check-side
survivor bits is 1.  When the variable boundary bit is 1, exactly two are 1.

## 2. Residual degree data

The unique variable-side survivor sits on one active Equality variable.
Therefore one active variable has internal degree 2 and all other active
variables have internal degree 3.

The raw five-port interface before pinning the zero hole has:

```text
4 check-side boundary coordinates
1 variable-side boundary coordinate.
```

On the check side there are exactly two structural cases.

### Case A — zero hole overlaps one survivor check

One check carries two raw check-side boundary coordinates: one remains free and
one is pinned to zero.

Then the internal check degrees are

[
1,2,2,3,ldots,3.
]

### Case B — zero hole lies on a distinct check

The three survivor checks and the zero-hole check are distinct.

Then the internal check degrees are

[
2,2,2,2,3,ldots,3.
]

These are the only possibilities after E85 propagation.

## 3. t=1 is impossible before any semantic search

For (t=1),

[
a=4,qquad b=3.
]

The three variable internal degrees are

[
2,3,3,
]

so there are 8 internal incidences.

If the Tanner graph is C4-free, any pair of variables can share at most one
check.  There are only

[
inom32=3
]

variable pairs, so the total pair-intersection count across checks is at most 3.

On the other hand, if check (i) has internal degree (d_i), then the same
pair-intersection count is exactly

[
sum_i inom{d_i}{2}.
]

Every positive degree pattern on four checks with

[
1le d_ile3,qquad sum_i d_i=8
]

has

[
sum_i inom{d_i}{2}ge4.
]

Contradiction.

Therefore:

[
oxed{
p=1,h=1,t=1
	ext{ has no C4-free residual incidence geometry at all.}
}
]

This is stronger than failure to realize (U_{2,4}): the underlying
C4-free graph itself cannot exist.

## 4. t=2 exact census

For (t=2),

[
a=7,qquad b=6.
]

Fix the unique degree-2 variable as variable 0.  The variable degree sequence is

[
(2,3,3,3,3,3).
]

Up to relabeling of checks within equal-degree roles, the two complete
check-degree cases are:

```text
overlap:
  (1,2,2,3,3,3,3)

distinct:
  (2,2,2,2,3,3,3)
```

E86 generates every bipartite incidence matrix with those exact degree
sequences subject to

[
|N(u)cap N(v)|le1
]

for every pair of variables (u,v).  This is exactly the Tanner C4-free
condition.

No connectivity assumption is imposed on the propagated residual network:
conditioning can disconnect pieces even when the original cluster was
connected.

## 5. Complete normalized graph counts

The exact generator counts are

```text
hole overlaps survivor check :  1,440
hole distinct                : 17,280
------------------------------------
TOTAL                        : 18,720
```

For each residual graph, the raw exact Tanner boundary relation has five
coordinates: four check-side and one variable-side.

Every one of the four check-side boundary coordinates is then tried as the
zero-hole pin.

Hence the exact number of conditioned configurations tested is

[
18,720	imes4=74,880.
]

For each configuration E86 computes the full exact boundary relation directly
from ExactOne/Equality semantics and pins the chosen check coordinate to zero.

Result:

[
oxed{
	ext{conditioned }U_{2,4}*(Pcap R)	ext{ hits}=0.
}
]

This exclusion does not assume that the raw five-port relation is already a
delta-matroid.  It is therefore stronger than the minimum condition needed for
a matroid-minor obstruction.

## 6. Interaction with the E85 unrestricted witness

E85 gave an unrestricted 7-check / 6-variable witness with

[
p=1,qquad h=1,qquad t=2
]

whose five-port canonical matroid is nonbinary and whose deletion/pinning
produces (U_{2,4}).

E86 proves that **every** C4-free residual incidence matrix with the same
degree data fails to realize the conditioned six-state family.

Therefore the Tanner C4s in the E85 witness are not an incidental defect at
this size.  They are necessary.

This is the strongest representation-side evidence so far that source
linearity may truly enforce binary representability.

## 7. First open p=1,h=1 size

The next size is

[
t=3:
qquad
a=10,qquad
b=9.
]

The degree data become:

```text
variables:
  (2,3,3,3,3,3,3,3,3)

checks, overlap case:
  (1,2,2,3,3,3,3,3,3,3)

checks, distinct case:
  (2,2,2,2,3,3,3,3,3,3)
```

A naive labeled enumeration already grows sharply, so the next step should not
be a blind scale-up of E86.

The correct move is to derive a residual exchange-graph normal form analogous
to E84, using one of the six conditioned (U_{2,4}) states as a reference
cover.

## 8. Reference-state structure for E87

Choose a conditioned state with:

```text
variable survivor bit = 1
two of the three check survivor bits = 1.
```

Then the selected reference cover contains exactly (t) variables, including
the unique degree-2 boundary variable.

The remaining (2t) unselected variables form the residual side.

After removing the selected reference-cover variables:

* most checks have two residual variable neighbours and become ordinary
  residual edges;
* depending on whether the zero hole overlaps the internally active or an
  externally satisfied survivor check, exactly two residual degree-1 check
  incidences or an equivalent cubic special case remain;
* source C4-freeness again forbids parallel residual edges;
* every selected reference-cover variable induces a matching among the
  residual check-edges, by the same repeated-pair argument used in E84.

This suggests a much smaller cubic/near-cubic graph-plus-matching partition
census for (t=3), rather than enumeration of arbitrary 10x9 incidence
matrices.

## 9. Next killer-test — E87

```text
P1_H1_RESIDUAL_EXCHANGE_GRAPH_KILLER

Derive the exact residual graph normal form for p=1,h=1 from a reference
U2,4-twist state.

Then:

1. enumerate the complete t=3 residual graph topology classes;
2. enumerate only the matching partitions compatible with the reference cover;
3. test the remaining five boundary states exactly;
4. either exclude p=1,h=1 at 10x9, or freeze the first genuine C4-free
   conditioned U2,4 witness.
```

If the lane continues to die, seek an induction invariant on the residual
exchange graph rather than pushing the census indefinitely.

## 10. Companion replay

```text
experiments/r5_e86_p1_h1_conditioned_u24_c4free_killer.py
```

Frozen assertions:

```text
t=1:
  no C4-free incidence geometry exists.

t=2:
  overlap normalized graphs = 1,440
  distinct normalized graphs = 17,280
  total normalized graphs = 18,720
  zero-hole pins tested = 74,880
  conditioned p=1 U2,4 hits = 0.
```

Scientific status:

```text
E86 = EXACT P1_H1 EXCLUSION THROUGH T=2.

P1_H1_T1 = IMPOSSIBLE BY COUNTING.
P1_H1_T2 = EXCLUDED BY COMPLETE C4-FREE CENSUS.
P1_H1_T3_PLUS = OPEN.

LINEAR_RXC3_CONDITIONED_U24 = OPEN.
DIRECT_U24_THROUGH_12x12 = EXCLUDED BY E84.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED BY E81.
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
