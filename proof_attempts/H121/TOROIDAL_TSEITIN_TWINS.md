# H121 — exact high-treewidth toroidal Tseitin twins

## Status

`FORMALIZING`, reproducibility `R3`.

The construction and finite fixtures are exact. Independent review is still
required for promotion.

## Base graph

Fix a signed-incidence radius `R` and set

\[
m=8R+13.
\]

Let

\[
T_m=C_m\square C_m
\]

be the `m × m` toroidal grid. Use two disjoint copies of `T_m`.

Every graph edge is a Boolean variable. At every grid vertex `v`, impose the
Tseitin equation

\[
\bigoplus_{e\ni v}x_e=c(v),
\]

where `c(v)` is its charge. Since every torus vertex has degree four, one local
equation is encoded by the eight width-four clauses excluding assignments of
the wrong parity.

## Charge patterns

Choose vertices

\[
p=(0,0),
\qquad
q=((m-1)/2,0).
\]

The SAT member has charges:

```text
component 0: p,q
component 1: none
```

The UNSAT member has charges:

```text
component 0: p
component 1: p
```

Both formulas therefore contain exactly two charged local gadgets.

## Satisfiability

In one connected component, XOR all vertex equations. Every edge variable
appears twice and cancels, giving the necessary condition

\[
0=\bigoplus_v c(v).
\]

Thus an odd total charge makes the component inconsistent.

Conversely, when total charge is even, choose a spanning tree, set all non-tree
edges to zero, and process tree vertices from leaves to the root. The parent
edge of each non-root vertex is uniquely selected to satisfy that vertex. The
root equation holds because total charge is even.

Therefore:

```text
SAT member component charges:   (2,0) -> satisfiable
UNSAT member component charges: (1,1) -> unsatisfiable
```

The executable artifact constructs the even-charge assignment and verifies
every generated CNF clause exactly.

## Exact local equality

The two SAT charges in the same torus are separated by more than any
radius-`R` incidence view. Hence every rooted radius-`R` ball sees at most one
charged vertex gadget.

The uncharged torus encoding is translation invariant. A rooted ball is fixed
by:

1. the root subtype: horizontal edge variable, vertical edge variable, or one
   of the local clause sign patterns;
2. the translated positions of charged vertex gadgets whose clauses occur
   inside the ball.

The SAT and UNSAT formulas have exactly two charge gadgets total. Around each
one, the translated local contribution is identical. Because the two SAT
charge-influence regions are disjoint, their multiset union equals the union of
one charge region in each UNSAT component. Every remaining root has the
uncharged periodic signature.

Thus the complete translation-normalized signature multisets agree exactly.
These signatures are finer than rooted signed-ball isomorphism: equal
signatures provide an explicit torus translation preserving root subtype,
clauses, variables, and literal signs.

## High primal treewidth

The primal graph has one vertex for every torus edge variable. Two variables
are adjacent exactly when the corresponding torus edges share a grid vertex.
Therefore each component primal graph is the line graph `L(T_m)`.

The separate H122 transfer gives

\[
\operatorname{tw}(L(T_m))
\ge
\frac{\operatorname{tw}(T_m)+1}{2}-1.
\]

Using the exact 2026 result

\[
\operatorname{tw}(T_m)=2m-1
\]

for `m >= 5`, we obtain

\[
\operatorname{tw}(L(T_m))\ge m-1.
\]

A disjoint union takes the maximum component treewidth, so the full formula
also has primal treewidth at least `m-1`.

## Reproduction

```bash
python experiments/direct/toroidal_tseitin_twins.py --self-test
```

The self-test checks radii zero through four, including:

- exact generated clause semantics;
- explicit SAT assignment;
- odd-charge UNSAT obstruction;
- exact local signature multiset equality;
- exact primal-line-graph identity.

## Meaning

H118 showed that local indistinguishability alone survives on easy cycles.
H121 removes that escape: the identity output now has treewidth

\[
\Omega(m)=\Omega(\sqrt{N}),
\]

not `O(log N)`.

What remains is not construction but transfer: prove that every permitted
constant-pass compiler producing low treewidth must lose the componentwise
charge distribution. That is H123.

## Claim boundary

H121 does not prove such a factorization theorem and does not refute unrestricted
polynomial-time SAT algorithms or resolve `P` versus `NP`.
