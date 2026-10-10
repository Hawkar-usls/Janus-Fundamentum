# R5 E8 6I — Prefix Factor-Width / TDD Compression Currency

Date: 2026-09-23

Authority:
`SOURCE_BOUND_DONOR + EXACT_TSEITIN_BRIDGE + OPEN_JANUS_COMPILER_GATE__NO_D1_PROMOTION`

Parents:

- `R5_E8_6I_RANK1_POLY_DEFECT_BASIS_PASS_R2_SHIFT_2026-09-23_v1.0.md`
- `JANUS_KEYMASTER_TDD_CIRCUIT_TREEWIDTH_R2_DONORS_2026-09-23_v0.1`

## 1. Why this currency is different

Fixed primal/hypertree width has already been ruled out as a universal property of
the canonical JANUS XOR/AND factorization.

Tree Decision Diagrams (TDDs), introduced by Capelli, Choi, Mengel, Muñoz, and
Van den Broeck (SAT 2026), provide a different measure:

```text
factor width
=
maximum number of nontrivial subfunctions
seen across a vtree cut.
```

For a Boolean function f and a fixed vtree T, the smallest TDD respecting T has
size

```text
O(|X| * fw(f,T)).
```

Thus the currency is not bag cardinality itself, but the number of
**semantically distinct boundary behaviours**.

## 2. Source theorem used

Theorem 13 of Capelli et al. considers bottom-up compilation of

```text
F = c_1 AND ... AND c_m
```

along a fixed vtree T.

Let

```text
k
=
max_i fw(c_1 AND ... AND c_i, T).
```

Then the compiler runs in

```text
m * |X| * poly(k).
```

Therefore if one can construct a vtree T and clause order such that every prefix
has factor width polynomial in the original input length L, the entire TDD
compilation is polynomial.

This is strictly the theorem needed here; no bounded-treewidth assumption is
part of the statement of Theorem 13.

The same paper proves that bounded treewidth is one sufficient source of small
factor width, but does not claim it is necessary.

## 3. Exact bridge from the JANUS checker circuit

We already have

```text
XOR_AND_FIXED_BOOLEAN_CSP
->
BOOLEAN_XOR_AND_CHECK_CIRCUIT
```

exactly and in polynomial size.

Apply the standard Tseitin gate encoding to the checker circuit C.

For every gate g introduce one variable y_g and a constant-size CNF encoding of

```text
y_g <-> op_g(inputs(g)).
```

Finally require the output gate to be true.

Call the resulting formula

```text
TSEITIN_CNF_EQSAT.
```

Then

```text
C has a satisfying input
iff
Tseitin(C) is satisfiable.
```

Every satisfying Tseitin assignment projects to a satisfying assignment of C,
and gate values for a fixed input are deterministically reconstructible.

The transformation has linear size in |C| for bounded fan-in gates.

## 4. New exact source-backed composition

If, for every JANUS Tseitin CNF F, we can polynomially construct

```text
(vtree T, clause order pi)
```

such that

```text
max_i fw(prefix_i(F,pi), T)
<=
poly(|F|),
```

then Theorem 13 yields a polynomial-size TDD in polynomial time.

Since TDD supports polynomial-time model enumeration/model counting and standard
model navigation, SAT decision and witness extraction are polynomial in the TDD
size.

Hence the full candidate chain is:

```text
POLY_MULTIPLICATIVE_DEFECT_BASIS_ABSTRACTION
  -> XOR_AND_FIXED_BOOLEAN_CSP
  -> BOOLEAN_XOR_AND_CHECK_CIRCUIT
  -> TSEITIN_CNF_EQSAT
  -> [POLY PREFIX FACTOR WIDTH CERTIFICATE]
  -> POLY_SIZE_TDD_REPRESENTATION
  -> SAT_DECISION_WITNESS.
```

All arrows except the bracketed one are source-proved or elementary exact
polynomial transformations.

## 5. Active gate

Freeze:

```text
R5_E8_6I
JANUS_PREFIX_FACTOR_WIDTH_GATE_V1
```

Question:

Does every JANUS-generated Tseitin CNF admit a polynomial-time constructible
vtree and clause order for which all prefix conjunctions have polynomial factor
width?

A PASS requires:

1. one deterministic construction of T and pi;
2. a theorem bounding prefix factor width by L^c for a fixed c;
3. no semantic oracle to choose T or pi;
4. no exponential subfunction enumeration during construction;
5. direct compatibility with Theorem 13;
6. polynomial witness reconstruction.

## 6. Why this is not a disguised selector

The state being bounded is not a vector of per-clause sheet choices.

It is the quotient of partial assignments by equality of the residual Boolean
subfunction across a vtree cut.

Two exponentially different local histories may collapse to one state whenever
they induce the same residual function.

Thus this mechanism is a genuine **semantic boundary-signature compression
currency**.

## 7. Current ceiling

No polynomial factor-width bound is claimed for the JANUS family.

General Boolean functions can require exponential decision-diagram
representations, so the source theorem is only a donor.

The next mathematical work is to derive or falsify a polynomial bound for the
specific XOR/AND/Tseitin family.

```text
TSEITIN BRIDGE
=
PASS EXACT

TDD SOLVER TARGET
=
SOURCE PASS

PREFIX FACTOR-WIDTH COMPILER THEOREM
=
SOURCE PASS CONDITIONAL ON POLY k

JANUS POLY PREFIX FACTOR WIDTH
=
OPEN <<< NEW COMPRESSION-CURRENCY GATE

D1
=
EMPTY

P_VS_NP
=
OPEN
```
