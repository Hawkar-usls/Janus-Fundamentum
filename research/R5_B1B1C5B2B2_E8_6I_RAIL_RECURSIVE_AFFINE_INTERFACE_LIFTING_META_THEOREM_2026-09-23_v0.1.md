# R5 E8 6I — RAIL: Recursive Affine Interface Lifting Meta-Theorem

Date: 2026-09-23

Authority:
`JANUS_DERIVED_META_THEOREM__NOVELTY_NOT_CLAIMED__THREE_SHEET_INSTANTIATION_OPEN__NO_D1_PROMOTION`

Parent:

`R5_E8_6I_REPRESENTATION_CHANGE_BEFORE_RELAXATION_GATE_V1`

## 1. Why this donor is being created

As of 2026-09-23 no public follow-up was found that formalizes the recursive-AIP
idea announced in Barto--Hadek--Zhuk,
*Toward a Uniform Algorithm and Uniform Reduction for Constraint Problems*
(arXiv:2604.06335v1).

That paper explicitly states that AIP can be enhanced by a natural recursion,
that the idea is genuinely different from singleton and higher-level approaches,
and that formal results will appear separately.

JANUS therefore does **not** attribute the construction below to that paper.

This artifact defines a separate JANUS donor with an elementary proof contract.

Generic abstraction refinement / CEGAR is established prior art.
No novelty claim is made for the abstract refinement pattern itself.

The JANUS-specific purpose is to turn the missing global sheet-coherence problem
into one exact mathematical obligation:

```text
POLYNOMIAL OBSTRUCTION BASIS
FOR FAILED GLOBAL LIFTS.
```

## 2. RAIL state

Fix a constant recursion height `h`.

At level `r`, an input instance `I` has encoded size `L`.

RAIL requires the following polynomial-time interfaces.

### R1 — abstraction

For a set of already learned cuts `C`:

```text
Abs_r(I,C)
```

constructs an abstract instance `J`.

Every concrete solution `x` of `I` maps in polynomial time to an abstract
solution

```text
alpha_r(x)
```

of `J`.

Therefore `J` is an over-approximation of `I`.

### R2 — recursive abstract solver

For `r=0), `Solve_0` is a fixed polynomial-time exact solver.

For `r>0`, the abstract instance belongs to the class solved by
`RAIL_{r-1}`.

The solver returns either

```text
UNSAT
```

or one explicit abstract witness `q`.

### R3 — exact lifting attempt

```text
Lift_r(I,q)
```

returns either

```text
SOLUTION(x)
```

where `x` is a verified concrete solution of `I` mapping to `q`,

or

```text
SPURIOUS(c)
```

where `c` is a valid refinement cut.

### R4 — valid cut

A cut `c` is represented in polynomial size and satisfies:

```text
every concrete solution x of I
has alpha_r(x) satisfying c.
```

The current spurious witness `q` violates `c`.

Thus adding `c` never removes a concrete solution and always removes the
current abstract witness.

### R5 — polynomial obstruction basis

For each input `I), there is a canonical finite family

```text
B_r(I)
```

such that

```text
|B_r(I)| <= p_r(L)
```

for a fixed polynomial `p_r`.

Every non-liftable abstract witness is separated by at least one cut in
`B_r(I)`.

The lifting procedure returns such a cut.

It never returns a cut already present in `C`.

This is the critical compression currency.

### R6 — polynomial state growth

For every `C subseteq B_r(I)`:

```text
|Abs_r(I,C)|
<=
q_r(L)
```

for a fixed polynomial `q_r`.

All maps, cuts, witnesses, histories, and verification certificates have
polynomial encoding size.

## 3. RAIL algorithm

```text
RAIL_r(I):

    C := empty

    repeat:

        J := Abs_r(I,C)

        q := Solve_{r-1}(J)

        if q = UNSAT:
            return UNSAT

        result := Lift_r(I,q)

        if result = SOLUTION(x):
            verify x
            return SAT(x)

        if result = SPURIOUS(c):
            assert c in B_r(I)
            assert c notin C
            C := C union {c}
```

At level zero use the frozen polynomial base solver.

## 4. Meta-theorem

### R5_E8_6I_RAIL_POLYNOMIAL_OBSTRUCTION_BASIS_META_THEOREM_V1

Assume R1--R6 for levels `0,...,h`, where `h` is a fixed constant
independent of input size.

Then `RAIL_h` is an exact deterministic polynomial-time decision and search
algorithm for its input class.

### Soundness of SAT

RAIL returns SAT only after `Lift` returns a concrete witness `x` and
the verifier accepts it.

Therefore every SAT answer is correct.

### Soundness of UNSAT

Every learned cut is satisfied by the abstraction of every concrete solution.

Hence after any number of cuts:

```text
I SAT
=>
Abs_r(I,C) SAT.
```

Therefore if the exact lower-level solver returns UNSAT, the original instance
has no concrete solution.

### Termination

Every failed lift adds one previously unseen element of `B_r(I)`.

Therefore level `r` performs at most

```text
|B_r(I)| + 1
<=
p_r(L)+1
```

abstract-solver calls.

### Completeness

Assume first that `I` is satisfiable.

By over-approximation and validity of all learned cuts, the abstract instance
can never become UNSAT.

If RAIL has not yet returned a concrete solution, every returned abstract
witness is non-liftable and therefore adds a fresh basis cut.

After at most `|B_r(I)|` such cuts, no non-liftable abstract witness remains.

The next abstract witness must lift to a concrete solution.

Now assume `I` is unsatisfiable.

Every abstract witness is non-liftable.

By R5 it is removed by a fresh basis cut.

After all basis cuts have been added, no abstract solution can remain;
otherwise it would be a non-liftable witness separable by another basis cut,
contradicting exhaustion of the basis.

Thus the abstract solver returns UNSAT.

### Polynomial lifecycle

Let `T_r(L)` be the worst-case runtime at level `r`.

For fixed polynomials `p_r,q_r,s_r`:

```text
T_r(L)
<=
(p_r(L)+1)
*
(
  T_{r-1}(q_r(L))
  +
  s_r(L)
).
```

Since `h` is a fixed constant, finite composition and multiplication of
polynomials is polynomial.

The history contains at most a polynomial number of polynomial-size cuts,
witnesses, and certificates.

Therefore:

```text
T_construct
+
T_refine
+
T_recursive_solve
+
T_lift
+
T_reconstruct
+
T_verify
+
T_history

<=
poly(L).
```

QED.

## 5. Why this is useful for JANUS

RAIL does not assume that a single fixed affine relaxation solves the input.

It allows the affine/global abstraction to produce a spurious witness,
provided that failure of the lift yields a **new polynomially bounded
certificate**.

Thus the required new mathematical object is not

```text
a magical polynomial SAT solver,
```

but the narrower statement

```text
all failed global sheet lifts
have polynomially many canonical obstruction types.
```

This is a genuine compression-currency question.

## 6. Frozen three-sheet instantiation

Define the open gate:

```text
R5_E8_6I
THREE_SHEET_RAIL_POLYNOMIAL_OBSTRUCTION_BASIS_GATE_V1
```

Input:

the frozen exact three-sheet representation of arbitrary signed 3-CNF,
including one-state-per-original-variable coherence.

Required construction:

### A — abstract global state

Construct a polynomial-size affine/module/vector abstraction of the global
sheet/decoder compatibility state.

Direct fixed-k visible affine relaxation is already blocked; therefore this
abstraction must arise **after a representation change** and may carry
instance-specific auxiliary state.

### B — lift

Given an abstract state `q`, either reconstruct one globally coherent
A3/F2^2-compatible lift and then one Boolean satisfying assignment, or produce
a sound obstruction certificate.

### C — polynomial obstruction basis

Prove:

```text
# canonical obstruction certificates
<=
poly(L).
```

Every non-liftable abstract state must violate at least one certificate in
that family, and a violated certificate must be computable in polynomial time.

### D — cut verification

Each learned cut must have a polynomial-time proof that **every** genuine
global lift satisfies it.

### E — fixed recursion height

Any recursive quotient/fibre levels used by the donor must have a constant
height fixed by the finite carrier family, or another independently proved
polynomial global recursion bound.

## 7. Immediate falsifiers

Reject an attempted RAIL instantiation if:

1. a cut is merely a clause-selector nogood equivalent to enumerating sheet
   choices;
2. the number of possible cuts is exponential;
3. finding the next cut requires SAT or an NP-hard separation oracle;
4. recursion branches over all fibres instead of using one compressed
   lower-level solver;
5. the recursion height is input-dependent without an independent total
   polynomial bound;
6. an abstract UNSAT answer is not certified by an over-approximation;
7. a successful abstract witness has no polynomial reconstruction path.

## 8. Relation to current source landscape

- Barto--Hadek--Zhuk 2026 formally characterize higher-level affine/minion
  relaxations and explicitly announce a different recursive-AIP direction,
  but do not publish its definition or theorem in that paper.
- Brakensiek--Guruswami--Wrochna--Zivny's BLP+AIP algorithm already provides
  a source precedent for **refine support first, then apply affine
  relaxation**.
- Generic abstraction refinement is prior art.
- RAIL is therefore used as a JANUS composition donor, not as a novelty claim.

## 9. Current status

```text
RAIL META-THEOREM
=
PROVED GIVEN R1--R6

THREE-SHEET R1--R4
=
NOT YET CONSTRUCTED

THREE-SHEET POLYNOMIAL OBSTRUCTION BASIS R5
=
OPEN
<<< ACTIVE MATHEMATICAL BRICK

FIXED-K DIRECT AFFINE
=
BLOCKED

DIRECT CLAP
=
BLOCKED

DIRECT DELTA-MATROID OCCURRENCE SPLIT
=
BLOCKED

D1
=
EMPTY

P_VS_NP
=
OPEN
```
