# R5 E10A — Cubic-Origin Distinguished-f Minor Universalization

Date: 2026-09-25

Authority:
`JANUS_DERIVED_EXACT_DISTINGUISHED_F_MINOR_UNIVERSALIZATION_AFTER_PA0006__NO_TORSO_PLACEMENT_OR_GLOBAL_OBJECTIVE_CLAIM`

Authorizing audit:
`PA-0006-CUBIC-ORIGIN-TORSO-IMAGE`

Continuation of:
`NM-0010-CUBIC-ORIGIN-STAR-COCYCLE-DESIGN`

Parent scope:
`R5_E10A_CUBIC_ORIGIN_TORSO_IMAGE_GATE_V1`

Checker:
`experiments/r5_e10a_cubic_origin_distinguished_f_minor_universalization.py`

## 1. Purpose

PA-0006 isolated the exact image question left after the generic PA-0005
scope widening.  NM-0010 then characterized a full cubic parent intrinsically:

```
M([I+P+Q|1])
<=>
a spanning 3-regular multiset of 4-cocycles
all containing distinguished f.
```

The remaining question was whether a 3-connected two-row torso can be lifted,
by deletion/contraction extensions, to such a cubic parent.

This note proves a stronger statement:

> Every loopless binary matroid with a chosen distinguished nonloop element is
> a distinguished-f minor of a polynomial-size cubic parent
> `M([I+P+Q|1])`.

In particular every 3-connected binary target, hence every 3-connected
S8-containing two-row target of PA-0006, passes the star-cocycle **minor**
liftability test.

This theorem does **not** prove that an arbitrary target occurs as a literal
1/2/3-sum torso of the parent, and it does not preserve by itself the global
lower-bound-tight objective `shortest_f=n/3+1`.

## 2. Cocycle-space form of a minor

Let

```
P = M([H|1]),
```

where the rows of H are indexed by a set L and its ordinary columns by R.
For a row-selector vector `y in GF(2)^L`, the corresponding parent cocycle
has coordinates

```
x_r = <y,H_r>        for r in R,
x_f = <y,1>.
```

Partition ordinary elements into:

- `T`: retained output elements;
- `C`: elements to contract;
- `D`: elements to delete.

Deletion punctures the cocycle code, while contraction shortens it.
Consequently the cocycle space of the retained minor is exactly

```
{
  ((<y,H_t>)_{t in T}, <y,1>) :
  <y,H_c>=0 for every c in C
}.
```

Thus the minor-image problem is equivalent to realizing the target cocycle
space as the external behavior of a cubic binary factor graph, with
contracted ordinary columns acting as homogeneous ternary constraints and
deleted ordinary columns acting as ignored degree-completion outputs.

The puncture/shorten interpretation is source-bound through the binary-code
minor / binary-matroid minor correspondence used in PA-0006.

## 3. Target code and logical XOR circuit

Let N be a loopless binary matroid on ground set E and choose a distinguished
nonloop element `p in E`.

Let

```
Cstar(N) <= GF(2)^E
```

be its cocycle space.  Choose a generator matrix G for this space and view its
row coefficients as free input bits

```
z_1,...,z_r.
```

Every target coordinate `x_e` is a nonzero linear form in those inputs,
because N is loopless.

For every target coordinate build a binary XOR tree computing that linear
form.  Every gate is represented by the ternary homogeneous equation

```
a+b+c=0,
```

where c is the XOR of a and b.

Fanout is handled by physical copies of a logical signal and equality gadgets,
not by allowing unbounded occurrence degree.

The total number of gates and signal uses is
`O(|E| rank(N))`, hence polynomial.

## 4. Parity-neutral equality gadget

The key local gadget for two physical copies a,b is:

```
a + u + v = 0
b + u + v = 0
u + v + w = 0.
```

All three constraints have arity exactly three.

The first two equations imply

```
a=b.
```

Moreover,

```
u+v=a=b,
w=u+v=a,
```

and therefore the total parity of the three auxiliary variables is

```
u+v+w = 0.
```

Hence the gadget simultaneously:

1. enforces equality of the two signal copies;
2. introduces no net contribution to the global row-selector parity;
3. has maximum left occurrence degree three:
   u and v occur three times, w once, and each endpoint copy once.

Chaining these gadgets makes any number of copies equal while preserving this
parity-neutrality.

## 5. Encoding the distinguished element into the parent all-ones column

Assign every occurrence of every XOR-gate input/output and every retained
ordinary target output to a distinct physical copy of the corresponding
logical signal.

Choose the total number of physical copies of each logical signal so that:

```
number of copies is even
for every logical signal except x_p,

number of copies is odd
for the logical signal representing x_p.
```

At most one unused physical copy is needed to correct a parity.

Connect the copies of each logical signal by the parity-neutral equality
chain from Section 4.

For every target element `e != p`, create one retained ordinary parent
column incident with three equal copies of the logical signal `x_e`.
Its value is

```
x_e+x_e+x_e = x_e.
```

The distinguished target element p is **not** represented by an ordinary
column.  It will be represented by the parent distinguished column f.

On every assignment satisfying the contracted ternary constraints:

- all physical copies of a logical signal have its common signal value;
- every equality-gadget auxiliary triple has total parity zero.

Therefore the XOR of **all** left/row selector variables is

```
sum_{left variables} y
=
x_p.
```

But this XOR is exactly the coordinate of the all-ones parent column f.
Thus the parent distinguished element survives the minor as the prescribed
target distinguished element:

```
f <-> p.
```

This is the step that is missing from a generic sparse Tanner realization.

## 6. Cubic completion without changing the external behavior

At this stage every right node already present is of degree exactly three:

- each contracted XOR/equality constraint;
- each retained ordinary target output.

Every left variable has degree at most three.

Let the current bipartite graph have left side L and right side R0.
Since every right vertex has degree three,

```
3|R0| = sum_{v in L} deg(v) <= 3|L|,
```

so `k=|L|-|R0|>=0`.

If necessary, add disjoint neutral contracted triples

```
a+b+c=0.
```

Each such triple adds three left variables and one contracted right node,
increases k by two, and contributes zero to the total left parity on every
feasible assignment.

Add enough such triples that

```
k>=3.
```

For every left vertex define the degree deficit

```
d_v=3-deg(v).
```

Then

```
0<=d_v<=3,
sum_v d_v = 3k.
```

Introduce exactly k new **deleted** right vertices, each required to have
degree three.

The desired incidence matrix between the old left vertices and these k new
right vertices has row degrees `d_v` and all column degrees three.
Such a simple bipartite graph exists.  For the Gale--Ryser inequalities:

- for one row, `d_v<=3<=k`;
- for two rows, the degree sum is at most six and `6<=2k`;
- for at least three rows, the sum is at most the total `3k`.

Thus the degree sequence is bipartite-graphical; a standard bipartite
degree-sequence / flow algorithm constructs it in polynomial time.

These new right vertices are deleted in the target minor.  They impose no
constraint and change no retained coordinate.

After completion:

```
every left degree  = 3,
every ordinary right degree = 3.
```

Therefore the two sides have equal cardinality and H is a square binary
row/column-weight-three matrix.

## 7. Recovery of I+P+Q

The incidence graph of H is a 3-regular bipartite graph.

By the standard König line-colouring / 1-factorization theorem its edge set
is the disjoint union of three perfect matchings.

After relabelling one matching as the diagonal:

```
H = I + P + Q
```

for permutation matrices P,Q with pairwise disjoint supports.

Appending the all-ones column gives an exact JANUS cubic parent

```
M([I+P+Q|1]).
```

## 8. Exact minor theorem

### Theorem — DISTINGUISHED_F_CUBIC_MINOR_UNIVERSALIZATION

Let N be any loopless binary matroid and let p be a distinguished nonloop
element of N.

There is a polynomial-time construction of a square binary matrix H with
row and column weights exactly three, together with disjoint ordinary-element
sets C,D,T, such that for

```
P = M([H|1])
```

we have

```
N  ~=  P / C \ D
```

on the retained ground set

```
T union {f},
```

under an isomorphism sending

```
f -> p.
```

#### Proof

The contracted set C consists of all ternary XOR, equality, and neutral dummy
constraint columns.

The deleted set D consists of the cubic-completion right vertices.

For every `e != p`, the retained column `t_e in T` reads three equal
copies and hence equals the target coordinate `x_e`.

By Sections 4--5 the parent distinguished coordinate is exactly `x_p`.

Therefore the cocycle space of the retained minor is exactly
`Cstar(N)`.  A binary matroid is determined by its cocycle space, so the
retained minor is N with f mapped to p.

All construction steps have size polynomial in the target representation.
QED.

Since every 3-connected matroid is loopless, the theorem applies directly to
the active 3-connected S8-containing two-row targets.

## 9. Finite controls

The committed checker independently builds the ternary realization, performs
the shortening/puncturing calculation in cocycle space, completes the
bipartite graph to degree three, and compares canonical row spaces.

Development controls covered 760 random loopless binary cocycle spaces.
The final pre-commit regression covered 460 seeded instances with:

```
3 <= |E| <= 8,
1 <= rank(Cstar) <= 4,
random distinguished p.
```

The largest generated cubic parent in that regression had 219 ordinary
rows/columns.

Every instance satisfied:

```
TARGET COCYCLE SPACE
=
MINOR COCYCLE SPACE,

ROW DEGREE = 3,
COLUMN DEGREE = 3,
|ROWS|=|ORDINARY COLUMNS|,
f-coordinate = target distinguished coordinate.
```

The checker is finite evidence only; the proof is the construction above.

## 10. Source / anti-duplication status

PA-0006 already source-bound:

- puncturing / shortening as binary code-minor semantics;
- Forney normal realizations as a representation donor, explicitly not a
  matroid-minor theorem;
- cubic LDPC regularization as an adjacent donor;
- sparse fixed-minor richness as an adjacent warning.

A targeted re-check after NM-0010 located no published theorem matching the
strong statement above: polynomial distinguished-element-preserving minor
embedding of an arbitrary loopless binary matroid into a square (3,3)-regular
`[H|1]` parent.

The construction therefore remains a JANUS-derived theorem under the scoped
PA-0006 authorization.  It does not claim novelty for ternary XOR circuits,
König completion, or code-minor semantics separately.

## 11. Consequence and exact ceiling

The star-cocycle **minor-image** question is now closed in the universal
direction:

```
3-CONNECTED BINARY TARGET
+
DISTINGUISHED ELEMENT
->
POLYNOMIAL CUBIC-ORIGIN DISTINGUISHED-f MINOR
=
PASS.
```

Therefore none of the following can be a standalone minor-image invariant:

```
three-connectivity,
S8 presence,
two-row graphic-lift structure,
direct failure of a local cubic representation,
star-cocycle minor liftability.
```

However this theorem does **not** prove:

1. that an arbitrary target is a literal torso produced by the specific
   1/2/3-sum decomposition used by E10;
2. that its separator-conditioned costs are coupled to the target in the
   required decomposition position;
3. that the embedding preserves the global top-level equality
   `shortest_f=n/3+1`;
4. a deterministic solver for prescribed `GF(2)^2` shortest path.

Thus the next scientific object changes again.

Before new mathematics, governance must source-audit the exact difference

```
ARBITRARY DISTINGUISHED MINOR
vs
ACTUAL DECOMPOSITION INTERFACE
+
GLOBAL LOWER-BOUND-TIGHT OBJECTIVE COUPLING.
```

Freeze next required audit:

```
PA-0007
CUBIC-ORIGIN INTERFACE / GLOBAL-OBJECTIVE COUPLING
```

No new mathematics in that changed scope is authorized by this theorem alone.

## 12. Ceiling

```
FULL CUBIC PARENT STAR-DESIGN CHARACTERIZATION
=
PASS (NM-0010)

DISTINGUISHED-f STAR-COCYCLE MINOR LIFT
=
PASS UNIVERSALLY FOR LOOPLESS BINARY TARGETS

CUBIC-ORIGIN MINOR IMAGE AS STANDALONE LEVERAGE
=
EXHAUSTED

ACTUAL TORSO / DECOMPOSITION PLACEMENT
=
NOT PROVED UNIVERSAL

GLOBAL shortest_f=n/3+1 COUPLING
=
NOT TRANSFERRED

DETERMINISTIC GF(2)^2 PRESCRIBED SHORTEST PATH
=
NOT RESOLVED
```
