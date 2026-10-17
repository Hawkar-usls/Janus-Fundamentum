# R5 E9 — Projective F2^4 Five-Line Spread UNSAT Terminal

Date: 2026-09-29

Status: `JANUS_DERIVED_EXACT_POLYNOMIAL_UNSAT_SUBROUTER__NO_D1_PROMOTION`

Parents / active context:
- `research/R5_E9_INTEGER_PAIR_PROJECTION_2SAT_TERMINAL_AND_COMPLETENESS_FALSIFIER_2026-09-29_v1.0.md`
- `research/R5_E9_INTEGER_PAIR2_COMPLETENESS_FALSIFIER_AND_TRIPLE_MOD7_TERMINAL_2026-09-29_v1.0.md`
- current projective-line / kernel-signature residual in PR #510.

Checker:
- `experiments/r5_e9_projective_f2_4_five_line_spread_unsat_terminal.py`

Scientific ceiling:

```text
FIVE_LINE_F2_4_SPREAD_CERTIFICATE = POLYNOMIAL UNSAT TERMINAL
BOUNDED_CERTIFICATE_COMPLETENESS   = NOT PROVED
UNIVERSAL POLYNOMIAL DECIDER       = OPEN
E8_D1                              = EMPTY
P_VS_NP                            = OPEN
```

This note does **not** prove P=NP.  It adds a source-compatible global UNSAT
certificate to the current projective-line residual and sharply identifies the
next completeness question.

## 1. Frozen abstract projective-line gate

Let

\[
V=\mathbb F_2^k.
\]

The current kernel-signature/projective residual associates to source rows a
family of two-dimensional vector subspaces

\[
\mathcal L=\{L_1,\ldots,L_m\},\qquad \dim L_i=2.
\]

A candidate parameter / linear functional is represented by `t in V` under the
standard nondegenerate dot product, with hyperplane

\[
H_t=\{x\in V:\langle t,x\rangle=0\}.
\]

The active exact semantics has the form

\[
\boxed{
\text{SAT}\iff \exists t\;\forall i:\;L_i\not\subseteq H_t.
}
\]

Equivalently,

\[
\boxed{
\text{UNSAT}\iff \forall t\;\exists i:\;L_i\subseteq H_t.
}
\]

This note assumes that already-proved representation identity and contributes a
new sufficient UNSAT certificate inside it.

## 2. Five-line spread certificate

Suppose five source lines

\[
L_1,\ldots,L_5\in\mathcal L
\]

are contained in a common four-dimensional subspace

\[
U\le V,\qquad \dim U=4,
\]

and their nonzero points partition the nonzero points of `U`:

\[
\boxed{
U\setminus\{0\}
=\dot\bigcup_{i=1}^{5}(L_i\setminus\{0\}).
}
\]

Since a two-dimensional binary subspace has exactly three nonzero points, the
five source lines account for all

\[
5\cdot 3=15=2^4-1
\]

nonzero points of `U`.  This is exactly a binary 2-spread of `U`.

### Theorem SPREAD-UNSAT-1

Any projective-line instance containing such five source lines is UNSAT.

### Proof

Fix arbitrary `t in V` and put

\[
K=H_t\cap U.
\]

There are two cases.

### Case A: `t` vanishes on all of `U`

Then

\[
K=U,
\]

so every `L_i` lies in `H_t`.  Hence `t` is bad.

### Case B: `t|_U` is nonzero

Then `K` is a hyperplane of the four-dimensional binary space `U`, so

\[
\dim K=3,
\qquad
|K\setminus\{0\}|=7.
\]

For every `i`, the dimension inequality gives

\[
\dim(L_i\cap K)
\ge \dim L_i+\dim K-\dim U
=2+3-4
=1.
\]

Thus each spread line contributes either

```text
1 nonzero point  (intersection dimension 1)
```

or

```text
3 nonzero points (the entire line lies in K).
```

Because the five spread lines partition `U\{0}`, their intersections with `K`
partition `K\{0}`.  Therefore five numbers, each in `{1,3}`, sum to seven.
The only possibility is

\[
7=3+1+1+1+1.
\]

Hence exactly one spread line satisfies

\[
L_i\subseteq K\subseteq H_t.
\]

So every nonzero restriction `t|_U` is also bad.

Both cases show

\[
\forall t\in V\;\exists i\in\{1,\ldots,5\}:L_i\subseteq H_t.
\]

By the frozen projective-line semantics, the instance is UNSAT. QED.

## 3. A canonical F2^4 spread

Writing nonzero vectors of `F2^4` as integers `1,...,15` with XOR as addition,
one explicit spread is

```text
L1 = { 1,  2,  3}
L2 = { 4,  8, 12}
L3 = { 5, 10, 15}
L4 = { 6, 11, 13}
L5 = { 7,  9, 14}
```

Each triple has the form `{a,b,a xor b}`.  The five triples are pairwise
disjoint and partition `{1,...,15}`.

For the 15 nonzero linear functionals on `F2^4`, exactly one spread line is
contained in the corresponding hyperplane; for the zero functional, all five
are contained.  The executable checker replays this census exactly.

## 4. Deterministic polynomial recognition

A certificate consists of five indices of source lines.  For every 5-tuple:

1. verify each candidate is a two-dimensional binary subspace;
2. compute the rank of the union of generators and require rank exactly four;
3. enumerate the three nonzero points of each line;
4. require the five triples to be pairwise disjoint;
5. require their union to contain exactly 15 nonzero points.

Rank and XOR operations are polynomial in `k`.  Enumerating all five-tuples costs

\[
O(m^5\,\operatorname{poly}(k)).
\]

Therefore recognition of this UNSAT certificate is deterministic polynomial
time.  No SAT oracle, exponential truth table, or hidden enumeration of all
`2^k` functionals is used.

Witness/certificate verification is also polynomial: the verifier checks only
the five lines and the four-dimensional span identity.

## 5. Why this is global progress rather than local arity replay

The recent pair- and triple-projection stack shows that bounded local projection
consistency can remain complete on each small coordinate set while the source is
Boolean-UNSAT.  The certificate here is different:

```text
five source rows
-> one 4D projective subspace
-> a complete partition of all 15 nonzero directions
-> every dual hyperplane is hit by a whole source line
-> global UNSAT
```

The argument certifies coverage of **all** dual functionals without enumerating
them.  Its proof is finite-geometric and nonlocal.

## 6. Prior-art boundary

The surrounding finite-geometry language is standard: line families meeting or
lying in all prescribed higher-dimensional subspaces are instances of blocking,
q-Turan, and q-covering design questions.  This note makes no novelty or priority
claim for binary spreads themselves.  The JANUS contribution here is the exact
binding of a constant binary 2-spread certificate to the frozen projective-line
UNSAT semantics of the source carrier.

Relevant background includes q-covering / q-Turan design literature and work on
blocking higher-dimensional projective spaces by lines.  The theorem above does
not depend on an external classification theorem; it is proved directly.

## 7. Exact next gate

The certificate turns the open projective-cover problem into a much sharper
question.

Freeze

```text
R5_E9_SOURCE_LINE_COVER_BOUNDED_CERTIFICATE_GATE_V1
```

A PASS must prove at least one of the following for every source-generated UNSAT
projective-line residual:

1. **bounded certificate theorem** — some constant-size or `O(log n)` family of
   source lines already covers all dual functionals and is polynomially
   discoverable; or
2. **polynomial contraction theorem** — a larger irredundant cover admits an
   exact polynomial representation-changing contraction with witness lifting; or
3. **different universal global pivot** with SOUND + COMPLETE + TERMINATES +
   POLY + RECONSTRUCT.

A FAIL may be supplied by a source-valid infinite family of UNSAT instances whose
minimum line-cover certificate size grows superlogarithmically (or otherwise
precludes the proposed bounded enumeration).

Forbidden pseudo-progress:
- merely increasing local projection arity;
- enumerating all `2^k` functionals;
- assuming every cover contains a spread;
- treating a general q-covering existence bound as an algorithm for the
  source-generated family;
- promoting this sufficient terminal to a complete UNSAT characterization.

## 8. Ceiling

```text
F2^4 FIVE-LINE SPREAD
= EXACT GLOBAL UNSAT CERTIFICATE

CERTIFICATE SIZE
= 5 SOURCE LINES

DETECTION
= O(m^5 poly(k))
= DETERMINISTIC POLYNOMIAL

PAIR/TRIPLE LOCAL CONSISTENCY BARRIERS
= NOT REOPENED

BOUNDED SOURCE-LINE COVER CERTIFICATE FOR ALL UNSAT INPUTS
= OPEN

UNIVERSAL POLYNOMIAL SAT DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
