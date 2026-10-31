# R5 E9 — Rooted MFMC Syndrome Polynomial Terminal

Date: 2026-09-28

Status: `JANUS_DERIVED_SOURCE_BOUND_POLYNOMIAL_TERMINAL__ROOTED_F7STAR_FRONTIER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AUGMENTED_REGULAR_MATROID_SYNDROME_POLY_TERMINAL_2026-09-28_v1.0.md`
- `research/R5_E9_UNSAT_PRIME_TOWER_AUGMENTED_REGULARITY_COLLAPSE_2026-09-28_v1.0.md`

External sources:
- P. D. Seymour, *The matroids with the max-flow min-cut property*, J. Combin. Theory Ser. B 23 (1977), 189–222, DOI `10.1016/0095-8956(77)90031-4`.
- K. Truemper, *Max-Flow Min-Cut Matroids: Polynomial Testing and Polynomial Algorithms for Maximum Flow and Shortest Routes*, Math. Oper. Res. 12(1) (1987), 72–96, DOI `10.1287/moor.12.1.72`.
- K. Truemper, *Matroid Decomposition*, revised edition, Chapter 13, especially Theorems 13.4.5 and 13.4.6.

Scientific ceiling:

```text
THIS IS A STRICT EXTENSION OF THE AUGMENTED-REGULAR-MATROID TERMINAL.
REGULARITY IS NOT REQUIRED.

THE POLYNOMIAL TERMINAL APPLIES WHEN THE DISTINGUISHED SYNDROME ELEMENT e_b
IS NOT CONTAINED IN ANY F7* MINOR OF ITS CONNECTED BINARY MATROID COMPONENT.

THE SURVIVING SOURCE-GENERATED OBSTRUCTION IS THEREFORE ROOTED F7* THROUGH e_b,
NOT GENERIC NONREGULARITY AND NOT AN UNROOTED F7/F7* MINOR SOMEWHERE ELSE.

NO UNIVERSAL CONTRACTION OF ROOTED F7* IS PROVED HERE.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Exact-One to a rooted shortest-circuit problem

Let

```text
A in {0,1}^{n x n}
```

have every row and every column of weight three, and put

```text
b = 1_n.
```

Work over `F2` and form

```text
A_plus = [A | b].
```

Let `e_b` denote the last column and

```text
M_plus = M_F2(A_plus).
```

Give every original-column element weight one and `e_b` weight zero.

From the parent augmented-syndrome theorem:

```text
mu(A)
 = min{|supp(x)| : A x = b over F2}
 = minimum weight of a circuit of M_plus containing e_b.
```

For cubic square `A`, every parity solution has weight at least `n/3`, with equality exactly when every source row contains one selected column. Hence

\[
\boxed{A\text{ has an Exact-One witness}\iff \mu(A)=n/3.}
\]

This is the only source-specific step needed below.

## 2. First polynomial front end: parity consistency

Before invoking any matroid decomposition, solve

```text
A x = b over F2
```

by Gaussian elimination.

If inconsistent, return `UNSAT` immediately.

If consistent, then `e_b` belongs to a circuit of `M_plus`. Let `K` be the connected component of `M_plus` containing `e_b`. Every circuit containing `e_b` lies entirely in `K`, so all other components may be discarded for the rooted shortest-circuit objective.

Thus the remaining instance is a connected binary matroid `K` with special element `e_b`.

## 3. Seymour's rooted characterization

For a connected binary matroid `M` with special element `l`, Seymour's max-flow min-cut theorem, in the rooted form used by Truemper Chapter 13, identifies the class exactly as

\[
\boxed{
(M,l)\text{ is MFMC}
\iff
l\text{ is contained in no }F_7^*\text{ minor of }M.
}
\]

The obstruction is rooted: an `F7*` minor elsewhere in the matroid does not by itself disqualify the pair unless the special element survives into that minor.

Truemper Theorem 13.4.5 gives a polynomial algorithm deciding whether an arbitrary connected binary matroid with special element `l` has the MFMC property.

This is already strictly broader than regularity:

```text
regular binary matroid
=> no F7 and no F7* minor
=> rooted MFMC for every special element,
```

but the rooted MFMC class also contains nonregular examples, including `F7` with any special element.

## 4. Polynomial shortest circuit in the rooted MFMC class

Truemper Theorem 13.4.6 states that the following problem is polynomial on MFMC matroids:

```text
input:
  connected binary matroid M,
  special element l,
  nonnegative rational distances d_e;

output:
  a circuit C containing l minimizing sum_{e in C} d_e.
```

The constructive proof first obtains the polynomial MFMC decomposition. Regular pieces are solved by a totally-unimodular linear program, `F7` pieces by constant-size enumeration, and the 2-sum / Delta-sum composition recursively transports shortest-circuit values. The resulting construction is polynomial.

Apply this theorem to `K` with

```text
d(e_b)=0,
d(e)=1 for every original column element.
```

The optimum is exactly `mu(A)`.

Therefore:

### Theorem RMFMC-1

For every cubic square incidence matrix `A`, if the distinguished syndrome element `e_b` is contained in no `F7*` minor of the connected component of

```text
M_F2([A | 1])
```

that contains `e_b`, then Exact-One decision is deterministic polynomial time.

The algorithm is:

1. solve `Ax=1` over `F2`; if inconsistent, `UNSAT`;
2. restrict `M([A|1])` to the component containing `e_b`;
3. run the polynomial rooted-MFMC recognition algorithm;
4. if the pair is MFMC, run the polynomial shortest-circuit algorithm through `e_b` with weights `(1,...,1,0)`;
5. let the optimum be `mu`;
6. return `SAT` iff `3 | n` and `mu=n/3`.

No exponential enumeration of the affine coset or syndrome group occurs.

## 5. Witness reconstruction

The shortest-circuit algorithm is constructive: it returns a minimum circuit `C` containing `e_b`.

Set

```text
x_j = 1 iff original-column element j belongs to C.
```

Because `C` is a binary dependence containing `e_b`,

```text
A x = b over F2.
```

If its weight is `n/3`, the cubic incidence-count identity forces every row to contain exactly one selected original column. Thus

```text
A x = 1 over the integers,
```

and `x` is an Exact-One witness.

Direct integer multiplication verifies the witness in polynomial time.

## 6. Strict improvement over ARM-2

The earlier ARM-2 terminal required the entire augmented matroid to be regular.

RMFMC-1 only requires

```text
e_b is in no F7* minor.
```

Hence the following cases, excluded by ARM-2, may now be solved polynomially:

```text
M([A|1]) is nonregular because it has F7 structure,
but e_b is not contained in an F7* minor.
```

The arbitrary-size UNSAT prime tower is already even easier: its augmented matroids are regular. The new theorem says future hostile controls must defeat a strictly larger router.

## 7. New exact residual

After this theorem, generic nonregularity is not the live obstruction.

Freeze the gate

```text
R5_E9_ROOTED_SYNDROME_F7STAR_GLOBAL_CONTRACTION_GATE_V1
```

with required input condition

```text
A is source-generated cubic square Exact-One carrier,
Ax=1 over F2 is consistent,
K = component of M_F2([A|1]) containing e_b,
e_b belongs to an F7* minor of K.
```

A PASS must give one of:

1. an exact polynomial contraction/quotient removing at least one rooted `F7*` obstruction while preserving the minimum circuit-through-`e_b` threshold and polynomial witness lift;
2. a polynomial decomposition into constant-interface rooted pieces with a polynomial total state bound;
3. a stronger source-specific polynomial terminal covering every rooted-`F7*` source instance;
4. an end-to-end polynomial algorithm for the source carrier.

Forbidden pseudo-progress:

- merely locating an unrooted `F7` or `F7*` minor;
- branching on the seven elements of one rooted minor without a polynomial global branch bound;
- deleting/contracting minor elements without preserving the distinguished shortest-circuit objective;
- using generic binary-matroid shortest circuit as an oracle;
- treating constant obstruction size as constant total semantic state.

## 8. Anti-loop / ceiling

```text
EXACT-ONE
iff mu(A)=n/3
= PROVED

mu(A)
= MINIMUM WEIGHT CIRCUIT THROUGH e_b IN M([A|1])
= PROVED

ROOTED MFMC CHARACTERIZATION
= e_b IN NO F7* MINOR
= SOURCE-BOUND CLASSICAL THEOREM

ROOTED MFMC RECOGNITION
= POLYNOMIAL

SHORTEST CIRCUIT THROUGH e_b ON ROOTED MFMC
= POLYNOMIAL

ROOTED MFMC CUBIC EXACT-ONE TERMINAL
= PROVED / SOURCE-BOUND

REGULARITY REQUIREMENT
= STRICTLY RELAXED

SURVIVING MATROID OBSTRUCTION
= ROOTED F7* CONTAINING e_b

ROOTED F7* UNIVERSAL CONTRACTION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
