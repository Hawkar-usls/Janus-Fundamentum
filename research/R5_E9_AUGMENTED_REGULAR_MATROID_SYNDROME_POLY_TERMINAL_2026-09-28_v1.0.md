# R5 E9 — Augmented Regular-Matroid Syndrome Polynomial Terminal

Date: 2026-09-28

Status: `JANUS_DERIVED_SOURCE_BOUND_POLYNOMIAL_TERMINAL__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS IS A GENUINE DETERMINISTIC POLYNOMIAL TERMINAL FOR THE SUBCLASS WHERE
THE AUGMENTED BINARY MATROID M([A | 1]) IS REGULAR.

IT DOES NOT PROVE THAT EVERY LINEAR-CUBIC EXACT-ONE INSTANCE HAS A REGULAR
AUGMENTED MATROID.
IT DOES NOT PROVIDE A POLYNOMIAL RECURSION FOR THE NONREGULAR SIDE.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

External donor:
- Manuel Aprile and Samuel Fiorini, *Regular Matroids Have Polynomial Extension Complexity*, arXiv:1909.08539v2 (2019).
- Proposition 19 identifies cycles of a regular matroid represented by a totally unimodular matrix with supports of {-1,0,1}-kernel vectors.
- Their Theorem 20 gives, for every fixed matroid element `e`, an explicit extended formulation
  for the circuit dominant restricted to circuits containing `e`:

```text
P^up_circuit(M,e)
 = {x | exists y:
          -x <= y <= x,
          U y = 0,
          y_e = 1,
          -1 <= y <= 1}
 = conv{chi_C : C circuit of M, e in C} + R_+^E,
```

for a totally unimodular real representation `U` of the regular matroid.
Thus nonnegative linear optimization over circuits containing a prescribed element is polynomial by linear programming once a regular representation is available.

Polynomial recognition/decomposition/construction for binary regular matroids is classical from the constructive Seymour/Truemper regular-matroid machinery; the JANUS theorem below uses it only as the source-bound regularity front end.

## 1. Cubic Exact-One as minimum affine-coset weight

Let

```text
A in {0,1}^{n x n}
```

have every row and every column of weight exactly three.  Work over `F2` and put

```text
b = 1_n.
```

Define

```text
mu(A) = min{|supp(x)| : A x = b over F2, x in {0,1}^n},
```

with `mu(A)=+infinity` if the affine system is inconsistent.

For any parity solution `x`, each source row contains an odd number of selected columns, hence either one or three.  Let `t` be the number of rows containing three selected columns.  Double-count selected incidences.  Every selected column has source degree three, so

```text
3 |supp(x)| = (n-t)*1 + t*3 = n + 2t.
```

Therefore

\[
\boxed{|supp(x)| \ge n/3.}
\]

Equality holds iff `t=0`, i.e. iff every row contains exactly one selected column.
Consequently

\[
\boxed{A\text{ has a Boolean Exact-One witness}\iff \mu(A)=n/3.}
\]

This identity holds without linearity; only row/column weight three is used.

## 2. Augment by the syndrome element

Form the binary matrix

```text
A_tilde = [ A | b ]
```

and let `e_b` denote its last column / matroid element.  Let

```text
M_tilde = M_F2(A_tilde).
```

Give every original-column element weight one and `e_b` weight zero.

### Lemma ARM-1

`mu(A)` equals the minimum weight of a circuit of `M_tilde` containing `e_b`.

### Proof

If `x` is a parity solution, then

```text
A x + b = 0 over F2.
```

Hence

```text
D = supp(x) union {e_b}
```

is a cycle of the binary matroid and contains `e_b`.  Every binary cycle is a disjoint union of circuits; exactly one member of that disjoint union contains `e_b`.  Dropping all other circuits cannot increase the nonnegative original-column weight.  Thus there is a circuit containing `e_b` with weight at most `|supp(x)|`.

Conversely, if a circuit `C` contains `e_b`, binary dependence gives

```text
sum_{j in C-{e_b}} A[:,j] = b over F2,
```

so the characteristic vector of `C-{e_b}` is a parity solution with weight `w(C)`.
Taking minima in both directions proves the lemma. QED.

If no circuit contains `e_b`, then `e_b` is a coloop in its component and `Ax=b` is inconsistent, matching `mu(A)=+infinity`.

## 3. Polynomial terminal under augmented regularity

Assume `M_tilde` is regular.

A constructive regular-matroid algorithm recognizes this in polynomial time and supplies a regular/TU representation (or an equivalent Seymour decomposition).  Apply Aprile--Fiorini Theorem 20 to the distinguished element `e_b` and minimize

```text
sum_{j != e_b} x_j
```

over `P^up_circuit(M_tilde,e_b)`.

The formulation has polynomial size and all objective weights are nonnegative.  Therefore the optimum `mu(A)` is computable deterministically in polynomial bit time by standard rational linear programming.

If the restricted circuit polyhedron is infeasible, return `UNSAT`.
Otherwise:

```text
mu(A) = n/3  -> SAT,
mu(A) > n/3  -> UNSAT.
```

(The first branch automatically requires `3 | n`.)

### Witness reconstruction

At optimum, the circuit-dominant theorem provides a support containing a circuit through `e_b`.  A circuit through `e_b` can be extracted in polynomial time by ordinary binary-matroid dependence tests / greedy support minimization.  Its original-column characteristic vector solves `Ax=b` and has weight `mu(A)`.  When `mu(A)=n/3`, Section 1 forces every source row to contain exactly one selected column, so this vector is the required Exact-One witness.  Direct multiplication by the original integer incidence matrix verifies `Ax=1` in polynomial time.

### Theorem ARM-2

For cubic square Exact-One instances,

\[
\boxed{
M_{\mathbb F_2}([A\mid\mathbf1])\text{ regular}
\Longrightarrow
\text{Exact-One decision + witness construction is deterministic polynomial time.}
}
\]

The total cost includes regularity recognition/representation, LP construction and optimization, circuit extraction, witness reconstruction and direct verification.

## 4. Tiny exact controls

### SAT regular control

Take `A=J_3`, the `3 x 3` all-ones matrix.  Every row/column has weight three.
The augmented binary matroid has one rank-one parallel class, hence is regular.

```text
mu(A)=1=n/3,
```

so Exact-One is SAT (choose any one column).

### UNSAT regular control

Take

```text
A = J_4 - I_4.
```

Every row/column has weight three.  Over `F2`, the four original columns are independent and their sum is `b=1_4`, so `[A|b]` represents `U_{4,5}`, a corank-one regular matroid.  The only parity solution is the all-ones vector:

```text
mu(A)=4 > 4/3.
```

Hence the instance is Exact-One UNSAT.

These controls are deliberately not claimed to be linear-hypergraph hostile controls; they replay the new regular-matroid terminal itself.

## 5. Relation to the global JANUS frontier

This terminal is structurally different from the existing raw-nullity, separator, balanced-matrix and rank-3 matching islands.  Its currency is the excluded-minor / TU structure of the **augmented syndrome matroid** rather than a scalar rank or graph-width parameter.

It also exposes a precise nonregular frontier.  By Tutte's excluded-minor characterization, a binary matroid is regular iff it has no `F7` or `F7*` minor.  Therefore every source instance not solved by ARM-2 has an augmented syndrome matroid containing a Fano or dual-Fano minor.

That statement alone is NOT a recursion: deletion/contraction of a forbidden minor may branch or destroy the distinguished-syndrome semantics.  The next legitimate question is narrower:

```text
Can a source-generated F7/F7* minor containing or interacting with e_b
be turned into an exact constant-interface contraction with polynomial witness lift
and a strict global potential decrease?
```

No such universal contraction is claimed here.

## 6. Anti-loop / ceiling

```text
CUBIC PARITY MINWEIGHT LOWER BOUND
mu(A) >= n/3
= PROVED

EXACT-ONE
iff mu(A)=n/3
= PROVED

AFFINE SYNDROME MINWEIGHT
= MIN-WEIGHT CIRCUIT THROUGH e_b IN M([A|1])
= PROVED

AUGMENTED REGULAR MATROID
=> POLYNOMIAL DECISION + RECONSTRUCTION
= PROVED / SOURCE-BOUND TO REGULAR-MATROID CIRCUIT DOMINANT

NONREGULAR AUGMENTED MATROID
=> F7 OR F7* MINOR
= CLASSICAL STRUCTURAL BOUNDARY

F7/F7* EXACT CONTRACTION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
