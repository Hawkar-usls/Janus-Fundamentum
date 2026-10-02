# R5 E8 6I — XOR/AND Factorization and Structural R2 Donors

Date: 2026-09-23

Authority:
`ONE_DERIVED_EXACT_REPRESENTATION_EDGE + SOURCE_PROVED_TRACTABLE_SUBCLASSES + SCOPED_WIDTH_BARRIERS__NO_D1_PROMOTION`

Parent:
`R5_E8_6I_RANK1_POLY_DEFECT_BASIS_PASS_R2_SHIFT_2026-09-23_v1.0.md`

## 1. Exact factorization of the refined state

Input type:

```text
POLY_MULTIPLICATIVE_DEFECT_BASIS_ABSTRACTION
```

consists of:

1. an affine system over F2 in Boolean variables/moment variables;
2. a subset of multiplicative defects
   `z = x y`;
3. constants.

Every affine equation

```text
x_1 + ... + x_m = b
```

can be converted in O(m) size to a chain of ternary parity constraints using
fresh prefix variables:

```text
t_2 = x_1 + x_2
t_3 = t_2 + x_3
...
t_m = t_{m-1} + x_m
t_m = b.
```

Every multiplicative defect is exactly the ternary Boolean relation

```text
AND(x,y,z) iff z = x y.
```

Hence the entire refined state has an exact polynomial representation over the
fixed Boolean language

```text
Gamma_XA = { XOR_3, AND, constants }.
```

Call the resulting type

```text
XOR_AND_FIXED_BOOLEAN_CSP.
```

The transformation is equisatisfiable, polynomial-size, and witness-preserving.
Auxiliary XOR-chain values are uniquely reconstructible from the original
variables.

This does **not** imply tractability: the generic fixed language
`Gamma_XA` is outside Schaefer's tractable classes.

## 2. Donor A — bounded treewidth

Freuder's k-tree/partial-k-tree CSP result gives exact polynomial-time dynamic
programming for finite-domain CSP instances whose primal graph has fixed
treewidth k; the dependence is exponential in k and polynomial (indeed linear
for fixed domain/k in the classical statement) in the instance size.

Therefore, for each fixed k:

```text
XOR_AND_CSP_PRIMAL_TW_LE_K
->
SAT_DECISION_WITNESS
```

is a valid exact polynomial solver donor.

This donor is structural, not algebraic: it does not require XOR and AND to
share a Schaefer polymorphism.

## 3. Donor B — bounded hypertree width

Gottlob–Leone–Scarcello introduced hypertree decompositions and proved that:

- for every fixed k, bounded hypertree width is polynomially recognizable;
- CSP instances of fixed hypertree width are polynomial-time solvable.

Hence, for each fixed k:

```text
XOR_AND_CSP_HYPERTREE_WIDTH_LE_K
->
SAT_DECISION_WITNESS
```

is also a valid exact polynomial donor.

For our factorization all primitive constraints have bounded arity (at most
three, ignoring unary constants).

## 4. Killer-test: can the JANUS factorization have universally bounded width?

No.

### 4.1 Original incidence graph survives as a minor

Start from an arbitrary signed 3-CNF F.

Occurrence splitting gives one Boolean occurrence vertex per literal
occurrence. For each original variable, its occurrences are connected by the
affine repetition-code equality chain. Contract each such connected chain to
one vertex representing the original SAT variable.

For each clause, the XOR/AND factorization is a connected local gadget:

- multiplicative product variables attach to the corresponding occurrence
  variables;
- the parity-chain auxiliaries connect the clause-local product variables;
- local flip/product variables stay inside the same clause gadget.

Contract the connected internal part of each clause gadget to one clause
vertex.

After these contractions, every original variable-clause incidence edge is
present.

Therefore:

```text
INCIDENCE(F)
is a minor of
PRIMAL(XOR_AND(F)).
```

Treewidth is minor-monotone, hence

```text
tw(PRIMAL(XOR_AND(F)))
>=
tw(INCIDENCE(F)).
```

### 4.2 3-CNF incidence treewidth is unbounded

Take any family of bipartite subcubic walls. Their treewidth is unbounded.
Designate one bipartition as clause vertices. Degree-2 clause vertices can be
padded with fresh leaf variables so every clause has arity three; adding leaves
does not destroy the wall minor.

Thus there are 3-CNF formulas with arbitrarily large incidence treewidth.

Consequently the JANUS XOR/AND factorization does not admit a universal
constant primal-treewidth bound.

So:

```text
UNIVERSAL
XOR_AND_FIXED_BOOLEAN_CSP
->
XOR_AND_CSP_PRIMAL_TW_LE_K
for one fixed k

=
FALSIFIED.
```

## 5. Hypertree-width consequence

Every primitive relation in the factorized CSP has arity at most 3.

In a hypertree decomposition of width k, every bag is covered by at most k
hyperedges. Hence each bag contains at most 3k variables.

Therefore bounded hypertree width k implies primal treewidth at most 3k-1 for
this bounded-arity family.

Since the primal treewidth above is unbounded, hypertree width is also
unbounded over the full JANUS-generated family.

Thus:

```text
UNIVERSAL FIXED HYPERTREE WIDTH
=
FALSIFIED.
```

## 6. What survives

The structural donor algorithms are still useful for subclasses and for
recursive local pieces, but neither width measure can be the single global
compression currency for arbitrary 3-CNF.

The R2 question therefore sharpens to a decomposition currency that can handle
unbounded global treewidth while keeping each recursive/interface state
polynomial.

Candidates not closed by this note include:

- separators/interfaces whose boundary algebra is compact despite unbounded
  treewidth;
- rank-based dynamic programming with polynomially many boundary signatures;
- recursive quotient systems whose depth is fixed independently of input size;
- source-proved structured circuit/knowledge-compilation classes that are not
  equivalent to bounded treewidth on this family.

## 7. Ceiling

```text
POLY_MULTIPLICATIVE_DEFECT_BASIS
->
XOR_AND_FIXED_BOOLEAN_CSP
=
PASS EXACT

FIXED TREEWIDTH SOLVER DONOR
=
SOURCE PASS

FIXED HYPERTREE-WIDTH SOLVER DONOR
=
SOURCE PASS

UNIVERSAL FIXED TREEWIDTH
OF JANUS FAMILY
=
BLOCKED

UNIVERSAL FIXED HYPERTREE WIDTH
OF JANUS FAMILY
=
BLOCKED

R2 REFINED EXACT SOLVER
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
