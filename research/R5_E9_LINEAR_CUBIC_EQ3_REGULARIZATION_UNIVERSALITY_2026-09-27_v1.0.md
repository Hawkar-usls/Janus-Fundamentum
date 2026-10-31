# R5 E9 — Linear Cubic EQ3 Regularization Universality Bridge

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_KARP_REDUCTION__LINEAR_CUBIC_POSITIVE_1IN3_IS_NP_HARD`

Scientific ceiling:

```text
THIS CLOSES THE PREVIOUS EXACT-INTERSECTION HARDNESS GAP.
IT DOES NOT SUPPLY A POLYNOMIAL SAT DECIDER.
P_VS_NP = OPEN.
```

## 1. Purpose

The previous n3 complexity audit deliberately refused to infer NP-hardness for the exact simultaneous class

```text
3-uniform + 3-regular + linear + square.
```

This note closes that source-coverage gap by an explicit equality gadget and a direct polynomial reduction from Exact Positive / Cubic Monotone 1-in-3 SAT.

## 2. Gadget

Use terminals `t0,t1,t2` and auxiliaries `a3,...,a9`, identified numerically as vertices `0,...,9`.

The nine Positive-1-in-3 clauses are

```text
(2,5,6)
(1,4,7)
(5,7,9)
(0,3,7)
(4,6,9)
(2,4,8)
(3,8,9)
(0,5,8)
(1,3,6)
```

Every clause has size three. Terminals `0,1,2` have gadget-degree two. Every auxiliary `3,...,9` has gadget-degree three.

No unordered vertex pair occurs in two clauses. Therefore any two clauses intersect in at most one vertex: the gadget is linear.

## 3. Exact terminal relation

Let the Boolean variables be `x0,...,x9`. Each clause imposes ordinary integer equation

```text
sum(clause variables) = 1.
```

Exact row reduction of the nine equations gives the complete rational solution family

```text
x0 = x1 = x2 = x9 = q,

x3 = x4 = x5 = 1-r-q,

x6 = x7 = x8 = r,
```

with free rational parameters `q=x9` and `r=x8`.

Hence every Boolean solution satisfies

```text
t0=t1=t2.
```

Conversely both terminal values extend:

```text
q=1, r=0:
(1,1,1,0,0,0,0,0,0,1),

q=0, r=0:
(0,0,0,1,1,1,0,0,0,0),

q=0, r=1:
(0,0,0,0,0,0,1,1,1,0).
```

Thus the projected Boolean relation is exactly

```text
EQ3 = {000,111}.
```

There is one extension of `111` and two extensions of `000`; multiplicity is irrelevant for decision/search preservation.

## 4. Reduction from cubic positive 1-in-3 SAT

Take an instance Phi in which every clause contains exactly three distinct positive variables and every variable occurs in exactly three clauses. Such Exact Positive 1-in-3 SAT is NP-complete.

For every original variable `x` with its three clause occurrences:

1. replace the occurrences by fresh terminal copies `x_0,x_1,x_2`, one per old occurrence;
2. attach one disjoint copy of the gadget above, identifying its three terminals with those copies.

Keep every original clause, now written on its occurrence copies.

### Degree

Each terminal has gadget-degree 2 and exactly one external old-clause occurrence, hence total degree 3.
Every auxiliary has degree 3.
Every clause has size 3.

Because the source is cubic, the number of original clauses equals the number of original variables. Per source variable the construction adds 3 terminal variables + 7 auxiliaries = 10 variables and 9 gadget clauses, plus globally one old clause per source variable. Therefore the output has equal numbers of variables and clauses and is a literal `n_3` carrier.

### Linearity

- gadget clauses are internally linear;
- distinct variable gadgets are disjoint;
- after occurrence splitting, two old clauses share no variable copy;
- an old clause meets a given variable gadget in at most the one terminal copy assigned to that occurrence.

Therefore every pair of output clauses intersects in at most one variable.

### Exact semantic equivalence

If the source has a satisfying assignment, assign all three terminal copies of each source variable its source truth value and use any corresponding gadget extension. Every old clause and gadget clause is Exact-One.

Conversely, every satisfying output assignment has equal terminal copies inside each gadget, by Section 3. Collapse them to the source variable. Every retained source clause then has exactly one true source variable.

Hence

```text
Phi is satisfiable
iff
R(Phi) is satisfiable.
```

The construction has constant blow-up per variable and is deterministic polynomial time. Witnesses reconstruct by terminal collapse in linear time.

## 5. Theorem

### LINEAR_CUBIC_POSITIVE_1IN3_KARP_HARDNESS

There is an explicit deterministic constant-factor Karp reduction from Cubic Positive 1-in-3 SAT to Positive 1-in-3 SAT restricted simultaneously to

```text
3-uniform,
3-regular,
linear,
square incidence,
```

i.e. to perfect matching / parallel-class existence in linear `n_3` configurations.

Membership in NP is immediate. Therefore this exact linear cubic class is NP-complete.

Consequently a deterministic polynomial exact solver for the full linear cubic class decides an NP-complete problem in polynomial time and, combined with standard NP-completeness, implies `P=NP`.

## 6. Interaction with current JANUS endgame

This theorem removes the previous possibility that the E9 linear hard core was merely a strict unproved-easy side class.

The following E9 formulations are now genuinely P-vs-NP-scale on their full linear cubic scope:

```text
Ax=1 over Boolean x,
parallel class in an n3 configuration,
Hoffman coclique of size n/3,
affine-coset minimum weight n/3,
directed perfect-code normalization,
A-reduction semantic closure.
```

A polynomial universal closure of any exact formulation above, with polynomial construction and witness reconstruction, is sufficient for `P=NP`.

## 7. Checker

Executable regression:

`experiments/r5_e9_linear_cubic_eq3_regularization.py`

It verifies:

- degree sequence `(2,2,2,3,3,3,3,3,3,3)`;
- pairwise linearity;
- exact rational row-reduction consequences;
- exhaustive Boolean projection exactly `{000,111}`;
- the three listed extensions.

## 8. Ceiling

```text
EXACT LINEAR-CUBIC SOURCE HARDNESS GAP
= CLOSED

LINEAR CUBIC POSITIVE 1-IN-3
= NP-COMPLETE

POLYNOMIAL UNIVERSAL SOLVER
= NOT YET PROVED

P_VS_NP
= OPEN
```
