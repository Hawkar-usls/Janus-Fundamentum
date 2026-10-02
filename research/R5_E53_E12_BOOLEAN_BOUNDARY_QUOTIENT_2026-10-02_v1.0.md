# R5 E53 — E12 Boolean Boundary Quotient Recovery

Date: 2026-10-02

Status:
`EXACT_GADGET_STATE_ELIMINATION__17Q_TARGET_COMPRESSES_TO_TWO_RXC3_COPIES__HARDNESS_SURVIVAL_LOCALIZED`

Scientific ceiling:

```text
THIS NOTE IDENTIFIES EXACTLY WHERE THE R5 E12 NP-HARDNESS SURVIVES AFTER
COMPLETE LOCAL BOOLEAN ELIMINATION OF EACH 17-COLUMN GADGET.

ONE GADGET HAS EIGHT VALID INTERNAL EXACT-COVER STATES. AFTER ELIMINATING
ALL INTERNAL TARGET ELEMENTS, ITS SIX BOUNDARY PORTS COLLAPSE TO TWO BITS:

  a_j = whether all three unprimed source elements are covered locally,
  b_j = whether all three primed source elements are covered locally.

ALL FOUR PAIRS (a_j,b_j) in {0,1}^2 ARE LOCALLY REALIZABLE.

GLOBAL BOUNDARY CONSISTENCY IS EXACTLY
  R a = 1,
  R b = 1,
WHERE R IS THE ORIGINAL RXC3 INCIDENCE MATRIX.

THUS THE 17q-VARIABLE LINEAR TARGET COMPRESSES EXACTLY TO TWO INDEPENDENT
COPIES OF THE q-VARIABLE SOURCE PROBLEM. BECAUSE THE TWO COPIES ARE
IDENTICAL AND INDEPENDENT,
  target SAT iff source SAT.

LOCAL STATE COMPRESSION THEREFORE SHRINKS THE INSTANCE BY A CONSTANT FACTOR
BUT DOES NOT REMOVE NP-HARDNESS.

P_VS_NP = OPEN.
```

## 1. Orientation

The E12 target is an Exact-Cover instance written as a 3-uniform 3-regular linear
hypergraph.

```text
target elements = constraints / matrix rows,
target triples  = selectable variables / matrix columns.
```

Fix one gadget corresponding to a source RXC3 triple

```text
C_j={x_1,x_2,x_3}.
```

Its primed copy uses

```text
C'_j={x'_1,x'_2,x'_3}.
```

The gadget has 15 internal elements

```text
z_1,...,z_6,
z'_1,...,z'_6,
t_1,t_2,t_3
```

and 17 selectable target triples `L_1,...,L_5,L'_1,...,L'_5,D_1,...,D_7`.

## 2. Exact local module problem

Treat the six boundary elements

```text
x_1,x_2,x_3,x'_1,x'_2,x'_3
```

as ports.

Inside one gadget require:

```text
every one of the 15 internal elements is covered exactly once;
each boundary port may be covered zero or one times locally.
```

The companion checker exhaustively enumerates all `2^17` subsets of target triples
and keeps exactly those satisfying the internal exact-cover condition.

There are exactly eight valid local states.

## 3. Boundary signatures collapse to two bits

For every valid local state, the three unprimed boundary cover bits are equal:

```text
cover(x_1)=cover(x_2)=cover(x_3)=a_j.
```

Likewise the primed boundary bits are equal:

```text
cover(x'_1)=cover(x'_2)=cover(x'_3)=b_j.
```

Thus the six-port boundary signature is completely described by

```text
(a_j,b_j) in {0,1}^2.
```

All four pairs occur.

The exact local multiplicities are:

```text
(a,b)=(0,0): 3 internal states,
(a,b)=(1,0): 2 internal states,
(a,b)=(0,1): 2 internal states,
(a,b)=(1,1): 1 internal state.
```

For decision, multiplicity is irrelevant; the exact projected relation is simply

```text
boxed:
R_local={(0,0),(1,0),(0,1),(1,1)}={0,1}^2.
```

So there is no local coupling between the unprimed and primed source-choice bits.

## 4. Global unprimed consistency is the source RXC3 system

Let the RXC3 source have `q` elements and `q` source triples.

Introduce one unprimed gadget bit

```text
a_j
```

for every source triple `C_j`.

Take one original source element `x_i`. By the RXC3 promise it belongs to exactly
three source triples.

In the E12 target, the global boundary element `x_i` is shared by exactly those
three gadgets. Gadget `j` covers `x_i` locally iff

```text
a_j=1.
```

The target Exact-Cover requirement says `x_i` must be covered exactly once globally.
Therefore

```text
sum_{j: x_i in C_j} a_j = 1.
```

Let

```text
R in {0,1}^{q x q}
```

be the original RXC3 incidence matrix, with

```text
R_ij=1 iff x_i in C_j.
```

Then all unprimed boundary equations are exactly

```text
boxed:
R a = 1,
a in {0,1}^q.
```

This is the original RXC3 Exact-Cover problem.

## 5. Primed consistency is an independent second copy

The same argument on the primed boundary elements gives

```text
boxed:
R b = 1,
b in {0,1}^q.
```

Because every local pair `(a_j,b_j)` is allowed, there is no extra gadget coupling
between the two systems.

Hence the exact global Boolean boundary quotient is

```text
R a=1,
R b=1,
a,b in {0,1}^q.
```

It is literally two independent copies of the same source problem.

## 6. Exact equivalence

If the source RXC3 instance has a witness `a`, choose

```text
b=a.
```

For every gadget select any local internal state realizing `(a_j,b_j)`. Such a state
exists because all four local pairs are allowed.

All internal target elements are then covered once by construction, and all global
boundary elements are covered once because

```text
R a=R b=1.
```

So the target is SAT.

Conversely, any target Exact-Cover witness projects gadgetwise to bits `(a_j,b_j)`.
Global boundary coverage forces

```text
R a=R b=1.
```

Thus `a` alone is an RXC3 source witness.

Therefore:

### Theorem E12-BOUNDARY-QUOTIENT

```text
boxed:
E12 target SAT iff source RXC3 SAT.
```

More structurally:

```text
boxed:
complete local Boolean elimination of the 17q target variables leaves exactly two
independent q-bit RXC3 quotient systems.
```

## 7. Compression ratio and hardness localization

The linear target has

```text
17q
```

selectable target triples.

After exact gadget elimination, the boundary quotient has

```text
2q
```

Boolean bits, and because the two copies are independent and identical, decision
can be reduced to just one `q`-bit RXC3 instance.

So the reduction can be inverted as a constant-factor structural compression:

```text
17q target variables -> q source variables.
```

But the quotient is NP-complete in general.

This pinpoints the limit of purely local gadget compression:

```text
boxed:
LOCAL ELIMINATION REMOVES THE LINEARIZATION GADGET OVERHEAD BUT RECOVERS THE
ORIGINAL HARD GLOBAL LANGUAGE.
```

## 8. Relation to R5 E17

R5 E17 gives the rational-kernel analogue:

```text
ker(B)/K_local ~= ker(R) direct-sum ker(R),
nullity_Q(B)=2q+2 nullity_Q(R).
```

E53 gives the exact Boolean-state analogue:

```text
Boolean boundary quotient = {a:R a=1} x {b:R b=1}.
```

The two notes now agree at both levels:

```text
linear kernel freedom and Boolean witness freedom both project back to two source
copies after local gadget gauge/state elimination.
```

This is strong evidence that the surviving hardness is genuinely global rather than
an artifact of the E12 internal gadget.

## 9. Frozen q=6 benchmark

For the E17 fixture,

```text
q=6,
C_j={j,j+1,j+3} mod 6.
```

The source matrix `R` has

```text
det(R)=-9,
rank_Q(R)=6.
```

Since every row sum is three,

```text
R * (1/3)1 = 1.
```

Full rank makes this the unique rational solution:

```text
a=(1/3)1.
```

It is not Boolean. Therefore the source is UNSAT, and by the boundary quotient the
102-variable E12 target is UNSAT.

The companion checker verifies both the eight local states and this exact quotient
obstruction.

## 10. Full-rank source terminal

For any E12-shaped target whose recovered source matrix `R` is rationally full rank,
the quotient gives an immediate polynomial decision:

```text
solve R a=1 exactly over Q;
SAT iff the unique solution is Boolean.
```

Because `R1=3*1`, every full-rank square+cubic source has unique solution

```text
a=(1/3)1,
```

and is therefore UNSAT.

Thus E53 closes the entire full-rank E12-source sector after gadget recognition.

The unresolved E12 quotient hardness necessarily lies in singular source matrices,
where the affine Boolean intersection remains nontrivial.

## 11. Relation to E50 multiclaw firewall

Corrected R5 E50 shows every target variable-column in the E12 bridge has multiple
claw states:

```text
c(v) in {2,4,8}.
```

E53 explains what happens if one refuses to branch on those local states and instead
eliminates the fixed gadget exactly:

```text
dense local ambiguity -> two boundary bits per gadget -> source RXC3.
```

So E50 and E53 together identify the hard mechanism:

```text
local ambiguity is compressible,
but its global quotient remains NP-hard.
```

## 12. Updated frontier

After E53, further progress on E12-shaped instances cannot come from merely finding
a more efficient exact enumeration of one gadget interior. That work is already
complete.

The remaining quotient is the original square 3-regular RXC3 system

```text
R a=1,
a in {0,1}^q.
```

The next universal attack must therefore operate on the **global source quotient**:

```text
noncommuting permutation structure,
equitable count quotients,
global conflict languages,
source-aligned certificates,
or a new algebraic normal form.
```

In particular, any claimed universal polynomial method must demonstrate leverage on
singular RXC3 quotient instances, not only on the E12 internal gadget layer.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e53_e12_boolean_boundary_quotient.py
```
