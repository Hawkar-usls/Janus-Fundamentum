# R5 E9 — Coprime-Cover Phase Persistence and Sharp 3-Cover Repair

Date: 2026-09-26

Authority:
`JANUS_DERIVED_LABELLED_COVER_SPECIALIZATION_AFTER_PA0026__TRANSFER_DONOR_SOURCE_BOUND__NO_COMPLEXITY_CLAIM`

Authorizing audit:
`PA-0026-COPRIME-COVER-Z3-PHASE-TRANSFER`

Parent:
`PA-0025-FILTERED-HIGH-NULLITY-GRAPH-COVER-SOURCE-AUDIT`

Checker:
`experiments/r5_e9_coprime_cover_phase_persistence.py`

## 1. Labelled cover setting

Let Omega_tilde cover Omega with constant fiber size m and projection pi.

Let P_tilde,Q_tilde and P,Q be permutations satisfying

```
pi P_tilde = P pi,
pi Q_tilde = Q pi.
```

This is the exact labelled lift of the normalized two-permutation overlay.

A Z3 phase downstairs is

```
phi(Pi)=phi(i)+1,
phi(Qi)=phi(i)-1.
```

An upstairs phase satisfies the same equations for P_tilde,Q_tilde.

## 2. Pullback direction

If phi exists downstairs, then

```
phi_tilde = phi o pi
```

satisfies

```
phi_tilde(P_tilde u)
=
phi(P pi(u))
=
phi(pi(u))+1
=
phi_tilde(u)+1,
```

and similarly for Q_tilde.

Therefore every labelled cover of a phase-PASS base is phase-PASS.

No restriction on m is needed.

## 3. Fiber-transfer descent when 3 does not divide m

Assume an upstairs phase phi_tilde exists.

For i in Omega define the fiber sum in F_3:

```
S(i)
=
sum_{u in pi^{-1}(i)} phi_tilde(u).
```

Because P_tilde maps the fiber over i bijectively onto the fiber over P(i),

```
S(Pi)
=
sum_{u in pi^{-1}(i)} phi_tilde(P_tilde u)
=
S(i)+m.
```

Similarly

```
S(Qi)=S(i)-m.
```

If 3 does not divide m, multiplication by m is invertible in F_3.  Put

```
phi(i)=m^{-1} S(i).
```

Then

```
phi(Pi)=phi(i)+1,
phi(Qi)=phi(i)-1.
```

So the base phase exists.

Hence

```
boxed(
gcd(m,3)=1
=>
[ phase(base) iff phase(cover) ].
)
```

Contrapositively:

```
boxed(
phase FAIL downstairs
persists to every labelled cover
whose degree is not divisible by 3.
)
```

In particular every 2-group / 2^t-sheeted cover preserves phase FAIL.

This is the explicit fiber-sum specialization of the source-bound finite-cover
transfer principle audited in PA-0026.

## 4. The modulus-3 condition is sharp

Take any connected phase-FAIL base.

Define a three-sheeted labelled cover on

```
Omega x F_3
```

by

```
P_tilde(i,t)=(P(i),t+1),
Q_tilde(i,t)=(Q(i),t-1).
```

Then

```
phi_tilde(i,t)=t
```

is an upstairs phase.

So every base phase obstruction can be repaired by a 3-cover.

### Connectedness

Phase FAIL means there is a labelled closed walk downstairs whose total
increment in F_3 is nonzero; otherwise path integration from a root would give
a global phase.

Lift that closed walk to the canonical 3-cover.  It returns to the same base
coordinate with a nonzero fiber displacement.

A nonzero element generates F_3, so all three sheets over one base vertex lie
in one lifted component.  Base connectedness then reaches every fiber over
every vertex.

Thus:

```
boxed(
connected phase-FAIL base
->
canonical connected 3-cover that is phase-PASS.
)
```

The prime 3 is therefore exact, not an artifact of the proof.

## 5. Noncommutativity automatically persists upward

Suppose P_tilde and Q_tilde commute.

Applying pi gives

```
P Q pi
=
pi P_tilde Q_tilde
=
pi Q_tilde P_tilde
=
Q P pi.
```

Since pi is surjective,

```
PQ=QP.
```

Contrapositively:

```
boxed(
PQ != QP downstairs
->
P_tilde Q_tilde != Q_tilde P_tilde upstairs
)
```

for every labelled cover, regardless of degree.

So graph-cover construction cannot accidentally move a noncommuting base into
the commuting P-island.

## 6. Rational kernel injection

Let

```
A=I+P+Q,
A_tilde=I+P_tilde+Q_tilde.
```

For every base kernel vector z define the fiber-constant lift

```
z_tilde(u)=z(pi(u)).
```

Then

```
(A_tilde z_tilde)(u)
=
z(pi u)+z(P pi u)+z(Q pi u)
=
(Az)(pi u)
=
0.
```

The lift map is injective, hence

```
boxed(
dim_Q ker A_tilde
>=
dim_Q ker A.
)
```

This is the blockwise old-kernel fact already source-bound in PA-0025, written
directly in JANUS coordinates.

## 7. Superlog nullity survives polynomial-degree covers

Let a base family have sizes n_j and nullities d_j with

```
d_j = omega(log n_j).
```

Let the cover degrees satisfy, for one fixed constant C,

```
m_j <= n_j^C.
```

The lifted size is

```
N_j=n_j m_j
```

and old-kernel injection gives d_tilde_j >= d_j.

But

```
log N_j
=
log n_j + log m_j
<=
(C+1) log n_j.
```

Therefore

```
d_tilde_j / log N_j
>=
d_j / ((C+1)log n_j)
->
infinity.
```

Hence:

```
boxed(
superlog rational nullity
is preserved by polynomial-degree labelled covers.
)
```

This removes the earlier concern that a cover must necessarily manufacture new
zero modes.  It need not, provided its degree is polynomially bounded and the
base family already has superlog nullity.

## 8. Consequence for the filtered-survivor program

Suppose we first construct a connected cubic base family satisfying

```
nullity = omega(log n),
PQ != QP,
Z3 phase = FAIL.
```

Then every polynomial-degree 2-group labelled cover automatically preserves:

```
superlog nullity,
noncommutativity,
phase FAIL.
```

The remaining independent obligations are therefore:

1. obtain incidence girth >=10 using such polynomial-degree 2-group covers (or
   construct it already in the base family);
2. ensure a 10-cycle survives/appears so NM-0028 supplies the sparse induced
   conflict odd-hole geometry;
3. recheck any downstream P-island / MIS reductions on the resulting family.

## 9. Checker controls

The checker uses a literal 9-variable cubic source that is connected,
noncommuting and phase-FAIL.

It exhausts all 2^(18) additive Z2 labelled covers of that source and verifies:

```
phase FAIL persists,
noncommutativity persists,
old nullity does not decrease.
```

It also checks additive covers of degrees 4,5,7,8.

For the same base, the canonical 3-cover is verified connected and phase-PASS.

## 10. Verdict

Freeze:

```
NM-0029
COPRIME-COVER Z3 PHASE PERSISTENCE
=
PASS

PHASE PASS DOWNSTAIRS
->
PHASE PASS UPSTAIRS
FOR EVERY COVER
=
PASS

3 DOES NOT DIVIDE COVER DEGREE
->
PHASE PASS UPSTAIRS IMPLIES PHASE PASS DOWNSTAIRS
=
PASS

2-GROUP COVER PRESERVES PHASE FAIL
=
PASS

CANONICAL CONNECTED 3-COVER REPAIRS PHASE FAIL
=
PASS / SHARPNESS

NONCOMMUTATIVITY PRESERVED UPWARD
=
PASS

OLD RATIONAL KERNEL INJECTS
=
PASS / SOURCE-BOUND COROLLARY

POLYNOMIAL-DEGREE COVER PRESERVES SUPERLOG NULLITY
=
PASS

FILTERED SURVIVOR FAMILY
=
STILL OPEN

NEXT
=
R5_E9_POLYSIZE_2GROUP_HIGH_GIRTH_COVER_OR_BASE_FAMILY_GATE_V1

D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
