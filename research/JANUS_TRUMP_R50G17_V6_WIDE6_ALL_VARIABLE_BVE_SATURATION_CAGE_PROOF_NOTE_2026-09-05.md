# JANUS TRUMP R50G17 — V6 width-6 all-variable BVE saturation cage

R50G16 exhausted its frozen canonical 3024-source pullback family and found no exact RUP6 ancestry realizer. This does **not** prove impossibility: 2485 candidates failed pre-BVE cleanliness and all remaining 539 became terminal during post-DP R33 normalization. The correct response is to explain what an actually unsafe V7 trace would have to do differently.

R50G14 already proved that an unsafe V7 same-pivot trace must preserve all six variables after eliminating the distinguished pivot. Therefore the post-DP R33 phase cannot use unit, pure or BVE variable elimination. In particular the six-variable state immediately before RUP must be BVE-fixed for **every** remaining variable, not only for the eventual hub.

Let that state contain a width-6 clause

\[
R=(\ell_1,\ldots,\ell_6)
\]

on all six variables. Fix a literal \(\ell\in R\). Orient polarity relative to \(R\):

- \(p\): clauses containing \(\ell\), including \(R\);
- \(n\): clauses containing \(-\ell\);
- \(r\): distinct non-tautological resolvents on \(\operatorname{var}(\ell)\).

Because \(R\) already contains one literal of every other variable, resolving \(R\) with any opposite-polarity clause has only two outcomes. If that clause contains the complement of another literal of \(R\), the resolvent is tautological. Otherwise all surviving literals of the opposite clause are already present in \(R\), so the resolvent is exactly

\[
R\setminus\{\ell\}.
\]

Hence the entire `R x opposite` row contributes at most one distinct non-taut resolvent. The other \((p-1)n\) parent pairs contribute at most one each, so

\[
r\le 1+(p-1)n.
\]

If \(r<p+n\), eliminating this variable strictly reduces clause count: the BVE transform removes \(p+n\) clauses and adds fewer than \(p+n\) distinct resolvents. Since clause count is the first component of the frozen R33 measure, BVE would be accepted. Therefore BVE-fixedness forces

\[
r\ge p+n.
\]

Combining,

\[
1+(p-1)n\ge p+n
\]

or equivalently

\[
(p-2)(n-1)\ge1.
\]

For positive integers this gives

\[
\boxed{p\ge3,\qquad n\ge2.}
\]

This applies independently to all six literals of \(R\). Therefore every variable occurs at least five times in the pre-RUP state and

\[
\boxed{L\ge 6\cdot5=30}
\]

total literal incidences are mandatory. The all-variable width-6 clause itself contributes six, so the rest of the formula contributes at least 24.

At the minimal \(3\times2\) boundary, the `R` row must actually contribute its one non-taut resolvent: without it, the remaining \((p-1)n=4\) pairs cannot reach the five resolvents needed to avoid strict clause-count descent. Thus a minimal boundary also requires at least one opposite-polarity clause whose only sign disagreement with \(R\) is the eliminated literal.

This theorem does **not** yet make the sixfold saturation cage impossible. The next obligation is to pull this simultaneous six-variable incidence requirement back through a V7/W4 exact-DP ancestry and either force an existing certified door or construct an explicit source satisfying the full cage.
