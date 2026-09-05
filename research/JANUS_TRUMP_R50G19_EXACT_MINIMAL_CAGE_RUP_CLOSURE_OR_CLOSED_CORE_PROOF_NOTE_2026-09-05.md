# JANUS TRUMP R50G19 — exact-minimal cage: RUP closure or closed support core

R50G18 gives an explicit V7/W4 ancestry realizer of the complete R50G17 sixfold cage. The cage itself is therefore not impossible. In that witness, however, RUP destroys the cage and full same-pivot R47J terminates. R50G19 isolates the exact combinatorial mechanism behind that collapse.

## Exact-minimal cage

Let `H` be an R33-fixed six-variable state containing an all-variable width-6 clause

\[
R=(\ell_1,\ldots,\ell_6).
\]

Assume every variable is exactly on the R50G17 minimum:

\[
p_i=3,\qquad n_i=2,
\]

with BVE blocked.

For each literal \(\ell_i\), R50G17 gives

\[
r_i\le 1+(p_i-1)n_i=5.
\]

BVE-fixedness requires \(r_i\ge p_i+n_i=5\), so equality holds throughout. In particular the resolution row using `R` itself must contribute its one possible non-tautological resolvent.

Therefore there exists at least one opposite-polarity clause

\[
D_i=(-\ell_i\vee S_i)
\]

whose remaining literals contain no complement of any other literal of `R`. Since the formula has exactly the variables of `R`, every literal in \(S_i\) has the **same polarity as R**. Since the state is unit-fixed, \(S_i\ne\varnothing\).

A single clause cannot be such a row witness for two different heads: if it contained both \(-\ell_i\) and \(-\ell_j\), resolving it with `R` on \(\ell_i\) would leave both \(\ell_j\) and \(-\ell_j\), making the resolvent tautological. Hence row witnesses for different heads are distinct.

## Support hypergraph

Create one directed hyperedge

\[
S_i\to i
\]

for every row witness `D_i=(-l_i OR S_i)`.

Interpret a set `K` of vertices as literals of `R` already forced false. If the support of a witness is contained in `K`, its clause becomes unit and forces its head literal of `R` false as well. Thus define the monotone closure operator

\[
T(K)=K\cup\{i:\exists(S\to i),\ S\subseteq K\}.
\]

Iterating `T` reaches a unique finite fixpoint in at most six head additions.

## Dichotomy

Take any witness edge `S -> i` and start with the assumptions that make every literal in `S` false. Equivalently the initial false-variable set is `K_0=S`.

If the closure reaches all six vertices, ordinary unit propagation through the witness clauses forces every literal of `R` false. Then the all-variable clause `R` becomes empty and yields conflict. Therefore the candidate strengthening

\[
(-\ell_i\vee S)\longrightarrow S
\]

is a valid single-literal RUP strengthening, independently checkable by the frozen R35B UP replay.

If **no** witness seed reaches all six vertices, then every seed closure is a nonempty proper fixpoint `K`. By construction there is no witness edge `S -> j` with `j outside K` and `S subseteq K`. Hence `K` is an exact proper support-closed core.

So every exact-minimal sixfold cage satisfies the exhaustive alternative

\[
\boxed{\text{RUP full-closure witness}\quad\lor\quad\text{proper closed support core}.}
\]

No probability or search assumption enters this dichotomy.

## R50G18 control

The fixed R50G18 cage has the cyclic single-flip witnesses

```
(-2,3,4)
(-3,4,5)
(-4,5,6)
(-5,6,7)
(2,-6,7)
(2,3,-7)
```

For example the support `{6,7}` of `(-5,6,7)` starts a false-literal cascade through the cyclic witnesses until all six literals of `R=(2,3,4,5,6,7)` are false. The resulting UP conflict is exactly the kind of certificate used by RUP in R50G18.

The remaining universal obstruction is therefore no longer an arbitrary exact-minimal cage. It is a cage carrying a **proper support-closed core**. The next gate must either prove such a core incompatible with the rest of R33/BVE/BCE/R49H/R47J geometry or construct an explicit survivor containing one.
