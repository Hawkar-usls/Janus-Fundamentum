# H095 — disjoint-union amplification

## Status

`FORMALIZING`, reproducibility `R1`.

The finite graph construction and exact independence-number checks are
implemented. The Lovasz-theta additivity proof under the exact H093 SDP
normalization still requires independent review.

## CNF construction

Let \(F\) and \(G\) use disjoint variable sets. Their conjunction has the union
of the clause sets. In the clause-literal conflict graph:

- vertices are literal occurrences;
- same-clause edges remain inside a component;
- complementary-literal edges remain inside a component because variable
  names are disjoint.

Therefore

\[
C(F\land G)=C(F)\sqcup C(G).
\]

The implementation assigns each component a disjoint variable-number interval
and checks that the combined edge count equals the sum of component edge
counts.

## Alpha additivity

For disjoint graphs,

\[
\alpha(A\sqcup B)=\alpha(A)+\alpha(B),
\]

because an independent set is exactly the union of independent sets chosen in
both components. The finite implementation checks this using exact exhaustive
alpha on small fixtures.

## Theta additivity obligation

The required mathematical identity is

\[
\vartheta(A\sqcup B)=\vartheta(A)+\vartheta(B)
\]

for the H093 primal convention

\[
\max \langle J,X\rangle,
\quad \mathrm{Tr}(X)=1,
\quad X_{ij}=0\text{ on edges},
\quad X\succeq0.
\]

The standard block constructions must be written carefully because the trace
normalization couples the components. A complete proof should provide both:

1. a primal construction reaching the sum from component optimizers with the
   correct scaling and cross-block terms;
2. a dual construction proving the matching upper bound.

C011 does not silently substitute a remembered theorem for that derivation;
attack `A271` remains `INCONCLUSIVE` until the exact convention is audited.

## Amplification consequence

Once additivity is established, a single pair of equal-target conflict graphs
with opposite SAT labels and equal theta value can be repeated \(r\) times:

- clause counts scale by \(r\);
- alpha values scale by \(r\);
- theta values scale by \(r\);
- the family is generated uniformly by variable offsetting.

Thus H096 would provide the finite seed and H095 would provide the asymptotic
family required by H087/H078.

## Reproduction

```bash
python experiments/theta/disjoint_union.py --self-test
```

The executable artifact checks only graph disjointness and alpha additivity. It
does not claim to compute or verify theta additivity.
