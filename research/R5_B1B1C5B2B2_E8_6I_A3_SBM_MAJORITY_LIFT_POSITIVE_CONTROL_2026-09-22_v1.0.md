# R5 E8 6I — A3 semilattice-block-Mal'tsev majority-lift positive control

Date: 2026-09-22

Authority: `EXACT_LIFT_POSITIVE_CONTROL__STRICT_SUBCLASS_ONLY__NO_D1_PROMOTION`

## 1. Purpose

The Boolean 6I branches now have exact blockers:

- full single-ternary Boolean tractable-algebra catalogue;
- Boolean multi-sorted / multi-operation Fano control.

The next legitimate surface is a genuinely larger lifted domain with internal algebraic block structure.

This artifact freezes the first exact positive control of that form.

It does **not** solve arbitrary 3-SAT.

## 2. Source-bound algorithm donor

Primary algorithm donor:

Andrei A. Bulatov,
*Constraint Satisfaction Problems over semilattice block Mal'tsev algebras*,
arXiv:1701.02623.

The source defines a semilattice block Mal'tsev algebra by:

- a congruence `sigma`;
- a binary operation whose quotient operation on `A/sigma` is a semilattice;
- projection behaviour of that binary operation inside every congruence block;
- Mal'tsev structure inside each block.

The source proves polynomial-time solvability of CSPs over semilattice block Mal'tsev algebras.

This is exactly the coarse-propagation + compact-algebraic-residual architecture required here.

Related donors:

- Bulatov–Jeavons multi-sorted algebraic CSP;
- few-subpowers / compact generating representations.

## 3. Frozen lifted algebra A3

Domain:

```text
D={0,1,2}.
```

Congruence blocks:

```text
B={0,1}
T={2}.
```

Define the binary operation `f` by:

```text
f(a,b)=a
if a,b in B,

f(a,b)=2
otherwise.
```

Thus on quotient blocks:

```text
B < T
```

and `f` induces Boolean join.

Inside each block, `f` is first projection.

Define the ternary operation `m` by:

```text
on B:
m(a,b,c)=a XOR b XOR c;

on T:
m(2,2,2)=2;

on mixed quotient blocks:
the output block follows the first argument block,
with the implementation frozen in the checker.
```

The checker verifies directly:

```text
A3/sigma under f
=
two-element semilattice

f restricted to each block
=
projection

m restricted to each block
=
Mal'tsev

sigma
=
compatible with f,m.
```

Therefore the frozen A3 satisfies the exact SBM structural conditions used by the source-bound polynomial algorithm.

## 4. Exhaustive local lift construction

Checker:

`research/tools/r5_e8_6i_a3_sbm_majority_lift_checker.py`

Frozen receipt:

`research/R5_B1B1C5B2B2_E8_6I_A3_SBM_MAJORITY_LIFT_POSITIVE_CONTROL_2026-09-22_v1.0.json`

The checker enumerates all subalgebras of:

```text
A3^3.
```

Exact count:

```text
2833.
```

It also enumerates every surjective decoder:

```text
pi:D->{0,1}.
```

There are exactly:

```text
6
```

such decoders.

For every one of the eight signed 3-clause relations and every decoder triple:

```text
(pi1,pi2,pi3)
```

the checker asks whether there exists a subalgebra

```text
S <= A3^3
```

whose coordinate-wise decoder image is **exactly** the signed Boolean clause relation.

Search size per signed clause:

```text
6^3
=
216 decoder triples.
```

Exact liftable count:

```text
108.
```

No random sampling or SAT oracle is used.

## 5. Exact decoder relation

For a decoder `pi`, define its coarse top-block bit:

```text
b(pi)=pi(2).
```

For a signed literal on coordinate j, interpret `b(pi_j)` through the clause sign.

The exhaustive classification gives the exact iff:

```text
signed clause has an A3 exact lift
iff
at least two of the three
signed coarse bits satisfy the literals.
```

Therefore the decoder-discovery relation is:

```text
AT_LEAST_2(l1,l2,l3).
```

And identically:

```text
AT_LEAST_2(l1,l2,l3)

=

(l1 OR l2)
AND
(l1 OR l3)
AND
(l2 OR l3).
```

So the complete prototype-discovery problem for this fixed A3 lift is ordinary 2-SAT.

Each value of the coarse bit has exactly three concrete surjective decoder realizations.

Hence the concrete decoder can be reconstructed after the coarse 2-SAT solution with constant work per variable.

## 6. Exact polynomial lifecycle on the admitted subclass

For an input 3-CNF F:

### Step A — build the coarse decoder formula

Replace each 3-clause by the three 2-clauses expressing the at-least-two condition.

Size:

```text
O(|F|).
```

### Step B — solve decoder discovery

Solve the resulting 2-SAT instance.

```text
T_discovery
=
poly(|F|).
```

### Step C — instantiate exact local lifts

For each signed clause and decoder triple, select a frozen subalgebra witness from the finite A3 lookup table.

```text
T_lift
=
O(|F|).
```

### Step D — solve the lifted CSP

Every lifted relation is a subalgebra of a power of the fixed SBM algebra A3.

Use the source-bound polynomial SBM CSP algorithm.

```text
T_lifted_solve
=
poly(|F|).
```

### Step E — decode

Apply the selected coordinate decoder to the lifted solution.

Because every lifted local relation has decoder image **exactly** equal to the original Boolean clause relation, the decoded tuple satisfies every clause.

```text
T_reconstruct+verify
=
poly(|F|).
```

Thus, on the admitted subclass:

```text
TOTAL LIFECYCLE
=
POLYNOMIAL.
```

No semantic-equivalence oracle, SAT oracle or hidden witness search occurs.

## 7. Exact scope of the subclass

The lift exists exactly when the original signed 3-CNF has a Boolean assignment such that:

```text
every clause has at least two true literals.
```

This is stronger than ordinary satisfiability.

It is recognized by the explicit 2-SAT decoder formula.

The strictness witness is:

```text
(x OR y OR z)
AND
(NOT x OR NOT y OR NOT z).
```

The original formula has:

```text
6
```

Boolean satisfying assignments.

But no assignment simultaneously gives at least two true literals in both clauses.

Therefore:

```text
A3_SBM_LIFT
=
STRICT_SUBCLASS

UNIVERSAL_3SAT_COVERAGE
=
FAIL.
```

## 8. Why this positive control matters

This is the first closed 6I object that realizes the desired architecture without hiding semantic choice:

```text
ARBITRARY INPUT SYNTAX
        |
        v
POLY-DISCOVERABLE COARSE CERTIFICATE
        |
        | 2-SAT
        v
EXACT LOCAL LIFT
        |
        v
TRACTABLE COARSE QUOTIENT
        +
MAL'TSEV RESIDUAL BLOCK
        |
        v
POLYNOMIAL LIFTED SOLVE
        |
        v
EXACT DECODER
```

The remaining defect is now a single exact logical gap:

```text
CURRENT COARSE CLAUSE CONDITION
=
AT_LEAST_2_OF_3

UNIVERSAL SAT NEEDS
=
AT_LEAST_1_OF_3.
```

This is substantially sharper than “find a better representation.”

## 9. Next exact theorem target

The next source-bound gate is:

```text
R5_E8_6I_LIFTED_SBM
THRESHOLD_2_TO_1_BRIDGE_GATE_V1
```

Find or rule out a polynomially described lifted algebra / finite family / multi-sorted structure for which every signed 3-clause has an exact lifted relation and:

```text
decoder/prototype discovery
=
POLYNOMIAL

clause admission
=
ordinary OR,
not majority/at-least-two

lifted consistency
=
POLYNOMIAL

reconstruction
=
POLYNOMIAL

total history
=
POLYNOMIAL.
```

A candidate that makes decoder discovery equal to original 3-SAT fails by the hidden-choice firewall.

## 10. Claim ceiling

```text
P_VS_NP
=
OPEN

D1
=
EMPTY

SUCCESSOR_ALGORITHM
=
LOCKED

A3_SBM_POSITIVE_CONTROL
=
PASS

A3_UNIVERSAL_COVERAGE
=
FAIL

CURRENT EXACT GAP
=
THRESHOLD 2 -> 1
```
