# R5 E9 — Binary-Kernel Bipartite Signed-Trade Donor

Date: 2026-09-27

Status:
`JANUS_DERIVED_STRUCTURAL_R5_R6_DONOR__NOT_UNIVERSAL__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_binary_kernel_bipartite_trade_donor.py`

Parents:
- `R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM_2026-09-24_v1.0.md`
- `R5_E9_TRANSLATION_STABILIZER_REPAIR_ACTION_CALCULUS_2026-09-23_v1.0.md`
- `R5_E9_WITNESS_DOMINANCE_EXISTENCE_COLLAPSE_AND_STRUCTURAL_TRANSFORMER_GATE_2026-09-23_v1.0.md`
- `R5_E9_R1_R5_SEMANTIC_ORACLE_HARDNESS_BARRIER_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS IS A POLYNOMIALLY CHECKABLE STRUCTURAL DONOR.
IT IS NOT A UNIVERSAL SELECTOR.
IT DOES NOT PROVE THAT A USEFUL TRADE EXISTS ON EVERY SURVIVOR.
IT DOES NOT PROVE P=NP.

D1 = EMPTY
P_VS_NP = OPEN
```

## 1. Setup

Let A be the clause-by-variable 0/1 incidence matrix of a positive
Exact-One-3 instance. For the cubic carrier every row and every column has
exactly three ones.

Take a binary vector

```text
c in ker_F2(A).
```

Let

```text
S = supp(c).
```

Because each row of A has exactly three entries and

```text
A c = 0 mod 2,
```

every clause intersects S in an even number of variables. Therefore every
clause intersects S in exactly

```text
0 or 2
```

variables.

## 2. Support multigraph

Construct a multigraph G_c as follows.

- vertices of G_c are the variables in S;
- for every clause containing exactly two variables u,v from S, add one edge
  uv labeled by that clause.

If the source instance is cubic, every selected variable v lies in exactly
three clauses. Since c_v=1, every incident clause must contain exactly one
other selected variable. Hence

```text
G_c is 3-regular as a multigraph.
```

This construction is linear-time once c is known.

## 3. Exact signed-lift theorem

We ask whether the binary kernel support can be lifted to an integer signed
kernel direction with unit magnitudes:

```text
h in {-1,0,+1}^n,
A h = 0 over Z,
supp(h)=S.
```

### Theorem BKT-1

The following are equivalent:

1. there exists h in {-1,0,+1}^n with A h=0 and supp(h)=S;
2. G_c is bipartite.

### Proof: 1 => 2

Take any clause touching S. By construction it contains exactly two selected
variables u,v. The third variable has h-value zero.

The integer equation on that row is therefore

```text
h_u + h_v = 0.
```

Since both values are nonzero and belong to {+1,-1}, they have opposite signs.
Thus the sign of h gives a proper 2-coloring of every edge of G_c. Therefore
G_c is bipartite.

### Proof: 2 => 1

Suppose G_c is bipartite. For every connected component choose a bipartition

```text
L dot-union R.
```

Define

```text
h_v = +1 for v in L,
h_v = -1 for v in R,
h_v = 0 outside S.
```

Every clause not touching S has row sum zero. Every clause touching S contains
one L vertex and one R vertex, so its row sum is

```text
(+1)+(-1)+0 = 0.
```

Hence A h=0 over the integers and supp(h)=S. QED.

## 4. Trade interpretation

Write

```text
S_plus  = {v : h_v=+1},
S_minus = {v : h_v=-1}.
```

Since A h=0,

```text
A 1_{S_plus} = A 1_{S_minus}
```

over the integers.

Because every touched clause contains exactly one plus and one minus variable,
S_plus and S_minus cover exactly the same set of clauses, once each.

Thus they form an exact-cover trade.

This gives a concrete conditional witness transformer:

if x is an Exact-One model satisfying

```text
x_v=1 for every v in S_minus,
x_v=0 for every v in S_plus,
```

then

```text
x' = x + h
```

is another Boolean Exact-One model.

The reverse move uses -h.

This is a genuine structural repair action. No SAT/UNSAT query is needed once
c and its bipartite support certificate are supplied.

## 5. Difference-of-models theorem

Let x and y be two distinct Exact-One models of the same instance and put

```text
h = y-x.
```

Then

```text
h in {-1,0,+1}^n,
A h = 0.
```

Let c be the binary support indicator of h. Reducing A h=0 modulo two gives

```text
A c = 0 mod 2.
```

Therefore c is a nonzero binary kernel word. By Theorem BKT-1, its support
multigraph G_c is bipartite, with the signs of h giving the bipartition.

### Corollary BKT-2

If an instance has two distinct Exact-One models, then its binary incidence
kernel contains a nonzero codeword with bipartite support multigraph.

Contrapositive:

```text
if every nonzero c in ker_F2(A) has non-bipartite G_c,
then the Exact-One instance has at most one model.
```

This is an exact uniqueness certificate direction. It is not an efficient
universal uniqueness test because enumerating all binary kernel words may be
exponential.

## 6. Polynomial donor from an explicit kernel word

Given one explicit c:

1. verify A c=0 mod 2;
2. construct G_c;
3. test bipartiteness by BFS;
4. if bipartite, synthesize h from the 2-coloring;
5. verify A h=0 over Z.

All five steps are polynomial.

A deterministic partial donor may therefore inspect any polynomially supplied
family of kernel words, for example a frozen RREF basis or another certified
polynomial candidate generator, and retain every bipartite-support word as a
signed trade.

Completeness is not claimed: a useful trade may exist only in a linear
combination of basis vectors.

## 7. Boundary-conditioned immediate contraction

The trade becomes a genuine dimension-dropping R5/R6 macro under one additional
structural condition.

For every touched clause, let w_e denote its third variable outside S. Suppose a
current residual state structurally certifies

```text
x_{w_e}=0
```

for every boundary variable of one connected component K of G_c.

Then every touched Exact-One equation reduces to

```text
x_u + x_v = 1
```

on the corresponding edge uv of K.

Because K is connected and bipartite, exactly two assignments on K are possible:
the two bipartition sides.

Hence the signed trade swaps the only two local states. We may canonically keep
one side, fix one chosen pivot variable, and reconstruct the discarded state by
adding +/-h.

This gives an admitted polynomial macro-step with immediate Boolean-dimension
drop whenever the boundary-zero certificate is already available.

The untouched WDR survivor does not generally provide those boundary pins, so
this theorem is a donor, not universal coverage.

## 8. Finite controls

The checker uses two cubic-linear controls.

### Fano plane

For the 7-variable Fano incidence matrix:

```text
|ker_F2(A)| = 8.
```

All seven nonzero codewords have weight four. Their support multigraphs are
non-bipartite. The checker independently confirms that no +/-1 signed lift exists
for any of them.

The Fano Exact-One instance is UNSAT.

### 3x3 affine control

For the 9-variable rows/columns/one-diagonal-class affine incidence system:

```text
|ker_F2(A)| = 4.
```

All three nonzero codewords have weight six and bipartite support multigraphs.
Each has an explicit signed trade lift.

The instance has exactly three Exact-One models; every pairwise model difference
is one of the signed trades predicted by the theorem.

The finite brute-force checks are OFFLINE_FALSIFIER_ONLY and are not part of an
E8 algorithm.

## 9. Relation to existing JANUS lanes

This donor is different from the already sealed XOR-translation stabilizer.

A global translation mask acts on every model by x -> x XOR c. Exact-One has
trivial local XOR stabilizer, so that action generally fails.

The present trade is conditional and integer-valued:

```text
x -> x+h
```

is applied only when Booleanity is preserved. It therefore belongs to the
conditional-repair / ranked-macro side of R5/R6, not to the exhausted global
translation-action lane.

It is also different from the cubic kernel-word normal form

```text
A z=0,
z in {-1,2}^n.
```

That normal form represents a complete Exact-One witness. The current h is a
model-difference / repair direction with alphabet {-1,0,+1}.

## 10. New active gate

Freeze:

```text
R5_E9_SIGNED_TRADE_COVERAGE_OR_REPRESENTATION_GATE_V1
```

Input:
a large-nullity WDR-surviving cubic-linear Exact-One state.

Attack:

1. compute polynomially available binary-kernel candidates;
2. lift every bipartite-support candidate to a signed trade;
3. test whether current structural boundary information makes any trade an
   immediate dimension-dropping macro;
4. if not, record the obstruction:
   - no polynomially found bipartite support,
   - or trade exists but boundary is not pinned,
   - or candidate generation itself is incomplete;
5. only then move to a richer representation.

A universal PASS would require an arbitrary-input theorem proving that every
nonterminal survivor either yields such a polynomially synthesizable applicable
trade or enters another proved-P carrier.

Nothing in this note establishes that coverage theorem.

## 11. Ceiling

```text
BINARY KERNEL WORD -> SUPPORT MULTIGRAPH
= EXACT

BIPARTITE SUPPORT
iff
SIGNED {-1,0,+1} INTEGER KERNEL LIFT
= PROVED

SIGNED LIFT
= EXACT-COVER TRADE / CONDITIONAL REPAIR ACTION

TWO DISTINCT MODELS
=>
NONZERO BIPARTITE-SUPPORT BINARY KERNEL WORD

BOUNDARY-ZERO CONNECTED TRADE
=>
TWO-STATE BLOCK + IMMEDIATE DIMENSION DROP

UNIVERSAL TRADE DISCOVERY / APPLICABILITY
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
