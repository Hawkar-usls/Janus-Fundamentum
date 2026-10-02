# R5 E9 — EXACT_ONE_3 projection-polymorphism / bounded-width barrier

Date: 2026-09-29

Status: `JANUS_DERIVED_ARBITRARY_ARITY_POLYMORPHISM_THEOREM__BOUNDED_WIDTH_LOCAL_CONSISTENCY_ROUTE_CLOSED__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVE P=NP AND DOES NOT PROVIDE A UNIVERSAL SAT DECIDER.
IT CLOSES THE ROUTE THAT TREATS THE EXACT_ONE_3 HARD CARRIER AS A
BOUNDED-WIDTH / FIXED-LOCAL-CONSISTENCY CSP.

IT DOES NOT CLAIM THAT EVERY GLOBALLY COMPUTED FIXED-ARITY INTEGER-LATTICE
SUMMARY IS EQUIVALENT TO ORDINARY LOCAL CONSISTENCY.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Template

Let

\[
R_{1/3}=\{(1,0,0),(0,1,0),(0,0,1)\}\subseteq\{0,1\}^3.
\]

This is the Boolean `EXACT_ONE_3` relation underlying the linear-cubic hard carrier.

We classify **every** finitary polymorphism of this single relation.

## 2. Set-function encoding of an arbitrary polymorphism

Let

\[
f:\{0,1\}^m\to\{0,1\}
\]

be an arbitrary `m`-ary polymorphism preserving `R_{1/3}`.
For every subset `S subseteq [m]`, define

\[
g(S):=f(\mathbf 1_S),
\]

where `1_S` is the characteristic vector of `S`.

Take any ordered partition

\[
A\sqcup B\sqcup C=[m].
\]

For each input index `r`, feed `f` one of the three tuples of `R_{1/3}` according to whether `r` belongs to `A`, `B`, or `C`.
Coordinatewise application of `f` produces

\[
(g(A),g(B),g(C)).
\]

Because `f` preserves `R_{1/3}`, this output must again belong to `R_{1/3}`. Hence, as an equality of ordinary integers,

\[
\boxed{g(A)+g(B)+g(C)=1}
\]

for **every** ordered three-partition of `[m]`.

## 3. The partition law forces finite additivity

Use the partition `([m], emptyset, emptyset)`. Since `g` is Boolean-valued,

\[
g([m])+2g(\varnothing)=1
\]

forces

\[
\boxed{g(\varnothing)=0,\qquad g([m])=1.}
\]

Now let `A,B` be disjoint and put

\[
C=[m]\setminus(A\cup B).
\]

The partition law gives

\[
g(A)+g(B)+g(C)=1.
\]

Apply it again to the partition `(A union B,C,emptyset)`:

\[
g(A\cup B)+g(C)+g(\varnothing)=1.
\]

Using `g(emptyset)=0` and subtracting yields

\[
\boxed{g(A\cup B)=g(A)+g(B)}
\]

for every pair of disjoint subsets.

Therefore

\[
g(S)=\sum_{i\in S}g(\{i\}).
\]

Since `g([m])=1` and every singleton value is in `{0,1}`, exactly one index

\[
i_*\in[m]
\]

has `g({i_*})=1`, and every other singleton has value zero.
Consequently

\[
\boxed{g(S)=1\iff i_*\in S.}
\]

But every Boolean vector is the characteristic vector of its support, so for every
`x in {0,1}^m`,

\[
\boxed{f(x)=x_{i_*}.}
\]

### Theorem E1P-1

Every finitary polymorphism of `EXACT_ONE_3` is a coordinate projection.

This is an arbitrary-arity theorem, not a finite polymorphism census.

## 4. Immediate algebraic consequences

The unary case says that the only endomorphism is the identity, so the template is a core.

Because all polymorphisms are projections, the template has no nontrivial weak-near-unanimity operations, no majority operation, no Maltsev operation, and no semilattice operation.

The bounded-width characterization of finite-domain CSPs therefore places this template outside bounded width: ordinary fixed-width local consistency cannot decide all `EXACT_ONE_3` instances.

This conclusion is algebraic and does **not** assume `P != NP`.

Source boundary:
- Libor Barto and Marcin Kozik, *Constraint Satisfaction Problems of Bounded Width*, FOCS 2009 / later JACM development;
- Marcin Kozik, *Solving CSPs Using Weak Local Consistency*, SIAM J. Comput. 49(6), 2020, DOI `10.1137/18M117577X`.

Only the general bounded-width characterization is imported. The projection-only classification above is derived directly for the frozen JANUS relation.

## 5. What this closes — and what it does not

Closed:

```text
EXACT_ONE_3 HAS HIDDEN WNU/MAJORITY/MALTSEV POLYMORPHISM
= FALSE

FIXED-WIDTH ORDINARY LOCAL CONSISTENCY IS A UNIVERSAL SOLVER
= FALSE

RAISE k-CONSISTENCY TO SOME OTHER FIXED CONSTANT k
= NOT A VALID UNIVERSAL ESCAPE
```

Not closed by this theorem alone:

```text
GLOBALLY COMPUTED LOW-ARITY INTEGER-LATTICE PROJECTIONS
= SEPARATE OBJECT

NONLOCAL REPRESENTATION-CHANGING CONTRACTION
= OPEN

GLOBAL INTEGER-LATTICE / GRAVER AUGMENTATION
= OPEN
```

The distinction is essential: an integer-lattice projection relation may be computed using the entire matrix via Smith/Hermite arithmetic, so it is not automatically identical to ordinary template-local consistency. Pair2 completeness is already falsified by a separate exact JANUS control; this theorem must not be misused as a blanket lower bound against every possible global summary.

## 6. Updated anti-loop rule

Do not spend future cycles searching for a fixed-arity polymorphism or a fixed local-consistency width of the raw `EXACT_ONE_3` language. Any successful universal polynomial mechanism must instead change representation globally, exploit source provenance after such a change, or solve the global integer-lattice augmentation problem.

## 7. Ceiling

```text
ALL FINITARY POLYMORPHISMS OF EXACT_ONE_3
= PROJECTIONS ONLY

BOUNDED-WIDTH LOCAL-CONSISTENCY ROUTE
= CLOSED

GLOBAL GRAVER / REPRESENTATION-CHANGING ROUTE
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
