# R5 E8 6I — Maximal Siggers-Certificate Discovery Hardness Control

Date: 2026-09-22

Authority: `SOURCE_BOUND_NEGATIVE_CONTROL__NO_GENERAL_LOWER_BOUND_BEYOND_CITED_FRAMEWORK`

## Sources

Primary source:

Rustem Takhanov,
*On the induced problem for fixed-template CSPs*,
arXiv:1708.08292v3.

https://arxiv.org/abs/1708.08292

Source used by Takhanov for the lifted-language / Siggers-pair statements:

Vladimir Kolmogorov, Michal Rolínek, Rustem Takhanov,
*Effectiveness of Structural Restrictions for Hybrid CSPs*,
ISAAC 2015 / arXiv:1504.07067.

https://arxiv.org/abs/1504.07067

## 1. Maximal tractability-certificate family

Takhanov Appendix B.6 defines `B_S` as the set of all Siggers pairs on the finite domain.

The source recalls the Siggers-pair characterization of finite-domain tractability and summarizes earlier lifted-language results:

```text
for any input structure R,

Gamma_R is tractable
iff
R -> Gamma^B_S;
```

and:

```text
CSP(Gamma)
is polynomial-time Turing reducible to
CSP(Gamma^B_S).
```

Takhanov then draws the consequence:

```text
if CSP(Gamma) is NP-hard,
then CSP(Gamma^B_S) is NP-hard.
```

This is the exact source statement used here.

## 2. Interpretation for the 6I search

`B_S` is the opposite extreme from the small Boolean `B4` family.

Its labels are rich enough to represent the existence of a general local finite-domain tractability certificate in the lifted language.

Thus:

```text
LOCAL TRACTABILITY CERTIFICATE COVERAGE
=
MAXIMAL WITHIN THE SIGGERS FRAMEWORK
```

but for an NP-hard template:

```text
PROTOTYPE DISCOVERY
=
NP-HARD.
```

For the full Boolean 3-SAT template this gives a source-bound hidden-hardness control.

## 3. Three anchors now frozen

### A. B4 / Boolean Bwnu

```text
prototype template
=
tractable for every Gamma

prototype->original solve
=
tractable

direct 3-SAT coverage
=
FAIL
```

### B. Constant value-coding algebras

```text
coverage
=
exact

prototype template
=
original Boolean template under renaming

discovery
=
original CSP
```

### C. All Siggers pairs

```text
tractability-certificate expressiveness
=
maximal source control

for NP-hard Gamma,
prototype discovery
=
NP-hard
```

## 4. Consequence

The 6I search must not proceed by monotonically enlarging `B` until coverage appears.

That strategy has a known failure mode:

```text
MORE CERTIFICATE EXPRESSIVENESS
can move the original hardness
into CSP(Gamma^B).
```

The missing mechanism must instead couple:

```text
A RESTRICTED TRACTABLE CERTIFICATE FAMILY
+
POLYNOMIAL EXACT PREPROCESSING
+
A COVERAGE THEOREM.
```

This is why the current positive target is a weak-relaxation / preprocessing theorem for a tractable induced layer, not an unrestricted search over all tractable algebras.

## 5. Claim ceiling

```text
GENERAL INDUCED-ALGEBRA ROUTE
=
NOT FALSIFIED

MONOTONE ENLARGE-B-UNTIL-COVERAGE ROUTE
=
BLOCKED BY SOURCE HARDNESS CONTROL

P_VS_NP
=
OPEN

D1
=
EMPTY

SUCCESSOR_ALGORITHM
=
LOCKED
```
