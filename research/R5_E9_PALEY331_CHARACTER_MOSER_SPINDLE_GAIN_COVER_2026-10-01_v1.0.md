# R5 E9 — Paley(331) Character Moser-Spindle Gain Cover

Date: 2026-10-01

Status:
`JANUS_EXACT_SOURCE_SPECIFIC_AF3_COVER_MOTIF__PALEY331_K4_FREE_BUT_MOSER_SPINDLE_POSITIVE__NO_D1_PROMOTION`

Scientific ceiling:

```text
This note gives a new exact AF3 cover certificate for the frozen q=331 member
of the Paley-orbit gradient-kernel family.  It is source-specific.  It is not a
universal SAT algorithm and it does not prove P=NP.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen source and the AF3-consistent branch

Use the already frozen Paley-orbit source with

```text
q = 331,
r = -2 mod q = 329,
O = <r> = {1,329,4,323,16,299,64,203,256,150,31,269,124,83,165},
L = ord_331(-2) = 15.
```

For a translation-invariant particular solution of `A r0 = 1` over `F3`, the
row equation gives

```text
2 r0(s) + r0(r s) = 1,
```

hence, because `2=-1` in `F3`,

```text
r0(r s) = r0(s) + 1.
```

Since `3 | L`, this recurrence closes consistently.  Fix the normalization

```text
r0(r^k)=k mod 3.
```

All affine solutions are written as

```text
r_{u->v} = r0(v-u) + c + p(v)-p(u),
```

with `c in F3` and a vertex potential `p` modulo the usual additive gauge.
A coordinate-zero hyperplane on an allowed arc `u->v` is therefore

```text
c + p(v)-p(u) = -r0(v-u).
```

For fixed `c`, put

```text
g_c(u,v) = -r0(v-u)-c
```

on every allowed oriented arc.  A selected edge set is balanced when there is
a gauge `h` with

```text
h(v)-h(u)=g_c(u,v)
```

on every selected oriented edge.  After the shift `q=p-h`, avoiding every
selected hyperplane is exactly proper 3-colouring of the selected underlying
graph.

Thus any balanced 4-chromatic subgraph is a valid cover certificate for that
`c`-slice.

## 2. The Paley19 K4 motif does not persist

The undirected support graph for the q=331 source is the Cayley graph on
`Z_331` with connection set

```text
O union (-O),
```

of degree 30.

A translation-normalized exhaustive check fixes one vertex at `0` and tests all

```text
C(30,3)=4060
```

triples of its neighbours.  No triple is pairwise adjacent.  Therefore the
support graph is `K4`-free.

So the q=19 three-gain-K4 certificate is not a universal motif even inside the
frozen Paley-orbit family.

## 3. A seven-vertex replacement: the Moser spindle

Let `M` have vertices

```text
X,A,B,U,C,D,V
```

and edges

```text
XA, XB, AB, AU, BU,
XC, XD, CD, CV, DV,
UV.
```

The first five edges form a diamond `K4-XU`; the next five form a second
diamond `K4-XV`; the last edge joins the two opposite tips `U,V`.

This graph is 4-chromatic.  Indeed, in every proper 3-colouring of a diamond,
the two nonadjacent tips must have the same colour.  Hence the first diamond
forces `X=U`, the second forces `X=V`, while the edge `UV` requires `U!=V`, a
contradiction.

## 4. Exact balanced spindle certificates for all three c-slices

The following triples give `(vertex, gauge h(vertex))` in `Z_331 x F3`.
All omitted arithmetic is modulo 331 for vertices and modulo 3 for gauges.

### c = 0

```text
X=(0,0)
A=(1,0)
B=(32,2)
U=(33,2)
C=(327,2)
D=(203,2)
V=(199,1)
```

### c = 1

```text
X=(0,0)
A=(1,2)
B=(300,2)
U=(301,1)
C=(256,0)
D=(248,2)
V=(173,2)
```

### c = 2

```text
X=(0,0)
A=(1,1)
B=(32,1)
U=(33,2)
C=(323,1)
D=(248,0)
V=(240,1)
```

For each slice and each of the eleven spindle edges, the checker verifies both:

1. the underlying difference lies in `O union (-O)`;
2. after orienting by the Paley-orbit direction, the displayed gauge satisfies
   `h(v)-h(u)=g_c(u,v)`.

Therefore every displayed spindle is balanced.  Avoiding all eleven coordinate
hyperplanes would give a proper 3-colouring of the Moser spindle, impossible.
Hence the eleven hyperplanes cover the complete fixed-`c` potential space.

Taking the three certificates together covers all three values of the constant
coordinate `c`.

## 5. This is not subset brute force

The executable regression contains a deterministic fixed-pattern extractor.
After translation/gauge normalization `X=(0,0)`, it works in the lifted gain
graph of degree `2L=30`:

1. enumerate adjacent pairs `A,B` in the lifted neighbourhood of `X`;
2. enumerate common neighbours `U` of `A,B` to obtain balanced diamonds;
3. repeat for a second diamond at the same `X`;
4. test the single closing edge `UV`.

For q=331 this returns a spindle in every `c`-slice.  The search is polynomial
for a fixed seven-vertex pattern and does not enumerate subsets of the 331
source vertices.

The q=331 instance also has

```text
zeta = r^(L/3) = (-2)^5 = 299 mod 331,
zeta^3 = 1,
zeta != 1,
zeta^2 = 31.
```

The first spindle already exposes these character-generated differences
(`1,31,299`) inside its first diamond.  This is the new structural clue to test
across the AF3-consistent Paley branch `3 | ord_q(-2)`.

## 6. Theorem

### PALEY331-CHARACTER-MOSER-COVER

For the frozen q=331 Paley-orbit Exact-One source:

```text
ord_331(-2)=15 and 3|15,
so A r=1 over F3 has the translation-character branch described above;
the support Cayley graph is K4-free;
for each c in F3 there is an explicit balanced Moser-spindle subgraph;
therefore each fixed-c AF3 potential space is covered by 11 coordinate-zero
hyperplanes, and the complete AF3 solution space is covered by the union of
three such certificates.
```

Consequently the Paley19 gain-K4 motif is not family-universal, but the broader
`balanced small 4-critical gain obstruction` mechanism survives at q=331.

## 7. Live frontier

The correct next target is no longer `K4` specifically.  Freeze:

```text
R5_E9_AF3_PALEY_CHARACTER_4CRITICAL_GAIN_OBSTRUCTION_GATE_V1
```

Test, on every AF3-consistent frozen Paley-orbit member with
`3 | ord_q(-2)`, whether a balanced 4-critical obstruction can be extracted in
polynomial time from multiplicative-character data.  In particular:

1. classify which character identities create balanced diamonds;
2. determine whether two such diamonds can always be joined into a bounded
   4-critical obstruction (Moser/Hajos type), or produce a counterfamily;
3. if bounded size fails, measure the minimum balanced 4-critical order as a
   function of `q` and `L`;
4. only promote a universal terminal after a symbolic family theorem and
   polynomial construction are proved.

## 8. Regression

Executable exact regression:

`experiments/r5_e9_paley331_character_moser_spindle_gain_cover.py`

It verifies:

- the order-15 `-2` orbit and the cubic root `zeta`;
- absence of any `K4` in the support graph by all 4060 normalized triples;
- all three explicit seven-vertex spindle certificates;
- exact gain compatibility on all 33 selected hyperplanes;
- 4-chromaticity of the spindle by exhaustive 3-colouring rejection;
- successful deterministic lifted-graph spindle extraction for `c=0,1,2`.

## 9. Ceiling

```text
PALEY331 AF3 CHARACTER BRANCH          = CONSISTENT
PALEY331 SUPPORT K4                    = NONE
BALANCED MOSER COVER c=0              = PROVED
BALANCED MOSER COVER c=1              = PROVED
BALANCED MOSER COVER c=2              = PROVED
FIXED-PATTERN EXTRACTOR                = POLYNOMIAL
FAMILY-WIDE BOUNDED 4-CRITICAL THEOREM = OPEN
UNIVERSAL POLYNOMIAL SAT SOLVER        = NOT PROVED
E8_D1                                  = EMPTY
P_VS_NP                                = OPEN
```
