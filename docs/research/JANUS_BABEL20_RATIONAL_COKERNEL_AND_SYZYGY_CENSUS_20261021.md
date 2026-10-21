# BABEL-20: exact correction ranks, source syzygies, and full-level barrier search

**Status: exact finite-instance advances, universal bound OPEN.** This checkpoint is experimental evidence for JANUS's rational Fourier-multiplier ideal system; it must not be renamed standard PSD SOS/Gram without equivalence proof. It does not establish P=NP.

## Main stratified experiment

[GitHub Actions rank survey #39596790448](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39596790448) independently verified nonzero modular minors for 15 connected legal rank-two covers from three sources. Five (B(\ker T)) maps have **full** rational anti-sector rank, while ten need additional analysis.

For eight cases with at most 11 unexplained directions, the [exact all-column Q audit #39597359928](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39597359928) constructed exact rational linear annihilators where needed, checked them against every legal generator, and established actual \(\operatorname{codim}_{\mathbb Q}B(\ker T)\) — not merely modular diagnostics.

| Frozen cover | Exact Q cokernel of B(ker T) | Independent source Koszul image | Koszul + same-column image |
| --- | ---: | ---: | ---: |
| SCL63 seed38 | 2 | 0 | 0 |
| SCL126_flip16 seed14 | 2 | 2 | 2 |
| SCL126_flip16 seed20 | 9 | 7 | 8 |
| SCL126_flip16 seed37 | 11 | 6 | 6 |
| SCL126_flip68 seed16 | 1 | 1 | 1 |
| SCL126_flip68 seed20 | 7 | 7 | 7 |
| SCL126_flip68 seed28 | 1 | 1 | 1 |
| SCL126_flip68 seed47 | 6 | 6 | 6 |

[Exact Koszul replay #39597823211](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39597823211) verifies source-zero polynomial identities and rational response ranks. [Same-source-column supplement #39599252532](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39599252532) checks all 142,509 equal-column collisions among 303,408 source coefficients of SCL126_flip16. It adds one rank direction for seed20; none for seed37.

### Important third outcome: target compatibility without surjectivity

For SCL63 seed38, the two-dimensional exact left-annihilator of B(ker T) pairs to **zero with every canonical lifted source degree-2 generator**, even though B(ker T) is not onto. It therefore pairs to zero with the residual of *any* existing rational SCL63 degree-2 base certificate, as does e0. The residual is consequently in the image of B(ker T), and a rational lifted certificate exists. This is a **target-compatible lift**, neither a full-rank kerT proof nor a Koszul rank repair. It is conditional on the already-frozen positive source certificate.

At present, these tests give sufficient degree-2 lift conditions for **11 of the 15** covers (five full kerT; five Koszul-complete; one target-compatible). The other four are not proven counterexamples: SCL63 seeds0/1 have large unresolved quotient, while SCL126_flip16 seeds20/37 have 1 and 5 residual directions after the two tested syzygy families.

## A general polynomial-size theorem with an explicit hypothesis

For n variables and n cubic rows, degree <=2 legal Fourier multipliers produce at most

\[
C=n\bigl(1+n+\binom n2\bigr)=O(n^3)
\]

integer matrix columns. Every column has <=4 positive integral entries counting multiplicity, so Euclidean norm <=4. If \(e_0\) lies in their rational column span, choose an independent spanning submatrix with rank \(R\le C\). A nonzero \(R\times R\) minor and Cramer's rule yield a solution with <=R nonzero terms; numerator/denominator absolute values are at most \(4^R\) by Hadamard, hence their bit lengths are \(O(R)=O(n^3)\). The sparse system itself has polynomial encoding size.

**This is only a conditional size theorem.** It does *not* prove that degree2 multipliers refute every legal UNSAT SCL. The necessary degree bound remains open. The existing JANUS formalism is a Fourier/ideal identity, not generic PSD SOS.

## Separate direct complete-M2 obstacle scout

[Independent new-cover search #39598546157](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39598546157) constructed twenty connected square cubic linear SCL21 incidences by connected Fano-block incidence switches. Exact GF2 enumeration: all twenty UNSAT. Modular test of the **full degree2 multiplier matrix M2** found zero nonmembership candidates. This does not prove a rational positive certificate for those twenty; it also produced **no exact rational full-M2 left-kernel witness**.

## NEXT: BABEL-21

1. Determine whether target residuals for SCL126_flip16 seeds20/37 lie in the known plus new source syzygy span. If not, search general \(\ker A\) relations and construct a bona-fide full degree2 left annihilator before any negative claim.
2. Resolve larger SCL63 seeds0/1 using sparse block/Schur reductions, not memory-heavy full dense elimination.
3. Generate legal independent non-cover families at growing n; seek an exact \(hM_2=0\) with \(h(e_0)\ne0\) *on every allowed row-multiplier column*. Only such a rational certificate rules out full historical JANUS degree4.
4. Compare correction ranks, number of syzygies, and exact determinant sizes across instances without extrapolating from finite samples.

Scientific authority remains frozen-instance only. Main branch and prior gates untouched.
