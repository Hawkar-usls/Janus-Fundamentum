# R5 E102 — Full Four-Candidate Local-Signature and Holonomy Firewall

Date: 2026-10-06

Status:
`E96_GLOBAL_EXTRAPOLATION_SUPERSEDED__RIGID_FREE_FAILURE_LOCALIZES_TO_BAD_HOLONOMY_COMPONENTS`

Scientific ceiling:

```text
E102 DOES NOT YET PROVE
  rigid-free TARGET6 parent => two coherent exchange rectangles.

IT FINDS AND FIXES A MISSING CASE IN THE E96 GLOBAL ARGUMENT:
target-derived kernel corrections can create a new triple-even defect at a
check that was exact for the base E95 parity candidate.

THE E96 LOCAL CLASSIFICATION OF THE 31 BASE DEFECTS REMAINS CORRECT.
THE SPECIFIC E96 GLOBAL CLAIM THAT, WITHOUT A RIGID DEFECT, FAILURE OF ALL
FOUR GLOBAL CANDIDATES REQUIRES ALL THREE PROPER-CONFLICT SIGNATURES IS
WITHDRAWN/SUPERSEDED BY E102.

E102 REPLACES IT WITH A COMPLETE CLASSIFICATION OF ALL 122 ORDINARY
SIX-WITNESS SUPPORT PARTITIONS AND A CONNECTED-COMPONENT HOLONOMY
LOCALIZATION THEOREM.

P_VS_NP = OPEN.
```

## 1. Why E102 audited E96 before proving a holonomy theorem

E95 constructs the base parity candidate for raw boundary state 8 by choosing
one exact witness for each of the six TARGET6 states and setting

```text
e_j = 1 iff variable j occurs an even number of times
      among the six chosen witnesses.
```

At an ordinary cubic check, the three incident variable supports partition the
six target labels.

Because the total support size is six, the three support cardinalities are
either

```text
even, even, even
```

or

```text
even, odd, odd.
```

Thus E95 correctly proved:

```text
* all-even -> base candidate selects all three variables: a defect;
* even/odd/odd -> base candidate selects exactly the even support: exact.
```

E96 then studied how the two target-derived kernel corrections repair the
all-even case.

The missing question was:

```text
Can the same correction break an even/odd/odd check that was already exact?
```

E102 answers YES.

Therefore a correct global analysis must classify every local support
partition, not only the 31 base defects.

## 2. The two target-derived corrections

Keep the E96 target labels

```text
0 = X_A
1 = X_B
2 = X_C
3 = Q_AB
4 = Q_AC
5 = Q_BC.
```

The two four-state XOR dependencies are

```text
D1={0,1,4,5}
D2={0,2,3,5}.
```

For a variable support S define

```text
h(S) = (
  |S cap D1| mod 2,
  |S cap D2| mod 2
)
in GF(2)^2.
```

For

```text
k=(a,b) in GF(2)^2,
```

the corrected E95 bit on S is

```text
e_k(S)
=
[|S| even]
xor
a h1(S)
xor
b h2(S).
```

For one ordinary check partition P=(S1,S2,S3), define

```text
Good(P)
=
{k in GF(2)^2 :
 e_k(S1)+e_k(S2)+e_k(S3)=1 }.
```

This is the exact set of the four canonical corrections that leave that check
ExactOne-correct.

## 3. Complete 122-partition classification

There are exactly 122 unordered partitions of six labeled target states into
three variable-support bins when empty bins are allowed.

E102 exhausts all 122.

Only 12 different Good-sets occur.

Let

```text
K = GF(2)^2,
K* = K - {0}.
```

For each nonzero direction a define the two affine hyperplanes

```text
H_a^0={k:k dot a=0},
H_a^1={k:k dot a=1}.
```

The exact table is:

```text
LOCAL TYPE                              COUNT

Good=empty                               5

Good=H_a^1                               6 for each of 3 directions
                                          =18 total

Good=K*                                  8

Good=K                                   28

Good=H_a^0                               9 for each of 3 directions
                                          =27 total

Good=K-{q}, q nonzero                    12 for each q
                                          =36 total
----------------------------------------------------
TOTAL                                    122
```

So:

```text
5+18+8+28+27+36 = 122.
```

## 4. What survives from E96

The all-even base-defect partitions are still exactly

```text
31 = 5 + 18 + 8.
```

They have:

```text
5 rigid opposite-pair coarsenings:
  Good=empty.

18 proper conflict defects:
  Good=H_a^1.

8 all-repair defects:
  Good=K*.
```

Therefore the E96 finite LOCAL classification is unchanged.

The correction concerns only its subsequent GLOBAL extrapolation.

## 5. The missing anti-conflict checks

Among base-good even/odd/odd checks, E102 finds three new restriction families

```text
Good=H_a^0.
```

These are the exact opposite of the E96 proper-conflict condition

```text
Good=H_a^1.
```

For the same nonzero direction a,

```text
H_a^0 cap H_a^1 = empty.
```

Hence two non-rigid locally legal checks can already eliminate all four global
E96 corrections:

```text
one base-good anti-conflict check H_a^0
+
one base-defect proper-conflict check H_a^1.
```

No three different proper-conflict directions are required.

Thus the former statement

```text
"without a rigid defect, global four-candidate failure requires all three
proper-conflict signature types"
```

is not a valid universal inference.

E102 supersedes that statement.

## 6. The other base-good restriction

The remaining nontrivial base-good signatures are

```text
Good=K-{q}
```

for one nonzero q.

These checks are initially ExactOne-correct but one specific nonzero correction
turns them into a triple-selected defect.

There are 12 support partitions for each excluded q.

Finally, 28 support partitions impose no restriction:

```text
Good=K.
```

## 7. Holonomy colors

For fixed chosen witnesses define on every active variable

```text
c(v)=(h1(v),h2(v)) in GF(2)^2.
```

Because D1 and D2 are zero-boundary XOR dependencies, h1 and h2 are genuine
GF(2) kernel vectors.

At every check:

```text
xor of incident c(v) = 00.
```

So the nonzero colors at one check are only of the forms

```text
a,a
```

or

```text
10,01,11.
```

All nonzero-colored variables incident with the same check therefore belong to
one connected nonzero-color component.

## 8. Component-wise kernel corrections

Let C be one connected component of nonzero-colored variables, with checks
used to connect them.

For any

```text
k in GF(2)^2
```

define the restricted correction

```text
z_C,k(v)=k dot c(v)
```

for v in C and zero outside C.

Since the color xor at every check is zero, z_C,k is itself a zero-boundary
GF(2) kernel vector.

Thus different nonzero-color components can choose their k values
independently.

This is strictly stronger than E96's four global candidates.

## 9. Why all-zero-color base defects are exactly rigid

Suppose

```text
c(v)=00.
```

Write d_i(v) for the parity with which support S_v intersects opposite atom
O_i.

Then

```text
h1=d0+d1=0,
h2=d0+d2=0,
```

so

```text
d0=d1=d2=t.
```

Also

```text
|S_v| mod2 = d0+d1+d2 = t.
```

Therefore if S_v is even, t=0.

Hence an even support with color 00 intersects every opposite pair evenly and
is exactly a union of complete opposite atoms: it is inert.

At a base E95 defect all three supports are even.

Therefore:

```text
boxed:
base defect + all three colors 00
iff
E96 rigid defect.
```

So in a rigid-free geometry, every remaining base defect lies inside a
nonzero-color holonomy component.

## 10. Correct rigid-free state8 criterion

For every nonzero-color component C, intersect the local allowed correction
sets of all ordinary checks touched by C:

```text
A_C = intersection Good(P_check).
```

Boundary checks cause no additional obstruction:

```text
* at A,B,C, a zero-boundary kernel correction toggles 0 or 2 internal
  incidences, so ExactOne is preserved;

* at E and the V-carrier x, both target-derived corrections are zero.
```

Therefore:

```text
boxed:
If the parent is rigid-free and every nonzero-color component C has
A_C nonempty, choose k_C in A_C independently.
```

The sum of the component-restricted kernel corrections then turns the E95
parity candidate into an exact raw-state-8 witness.

Consequently:

```text
boxed:
RIGID-FREE + NO RAW8
=>
THERE EXISTS A BAD HOLONOMY COMPONENT C WITH A_C=empty.
```

This is the correct universal residual frontier.

## 11. Minimal signature-level holonomy obstructions

Ignoring geometric realizability for one moment, use the 11 nonempty local
Good-set signatures and ask for inclusion-minimal families with empty
intersection.

E102 exhausts them:

```text
size 2 :  3 families
size 3 : 22 families
size 4 :  1 family.
```

The three smallest obstructions are exactly

```text
H_a^0 + H_a^1
```

for the three nonzero directions a.

So the first geometric killer is no longer the E96
"three different conflict signatures" pattern.

It is the much sharper signed phase clash:

```text
boxed:
Can one connected C4-free holonomy component contain both
an H_a^0 check and an H_a^1 check of the same direction?
```

If yes, freeze the first genuine TARGET6 realization.

If no, all two-check holonomy obstructions disappear and E103 moves to the
22 minimal three-signature patterns.

## 12. Relation to the E98 rectangle theorem

E98 remains valid.

Two coherent independent rectangles imply

```text
h1=h2=0.
```

Then there are no nonzero-color holonomy components at all.

E98's direct defect argument then gives

```text
no rigid defect => raw8.
```

E102 does not weaken that sufficient theorem.

What E102 changes is the attempted converse route:

```text
rigid-free
does NOT yet imply
two coherent rectangles.
```

Instead the precise obstruction to state8 is now a bad holonomy component.

## 13. E102-C — constructive B3 router identification

E100 already limits every B3 router relation to one Hamming layer:

```text
residue 0 : layer size 2,
residue 1 : layer size 3,
residue 2 : layer size 3.
```

The three canonical opposite-atom covers reveal at least one feasible boundary
state.

Let I be the set of distinct canonical states already seen.

Because the exact relation R obeys

```text
I subseteq R subseteq allowed layer,
```

the exact router type is determined by querying every unseen layer state.

Worst case:

```text
residue 0:
  at most 2-1 = 1 query.

residue 1 or 2:
  at most 3-1 = 2 queries.
```

Hence:

```text
boxed:
EXACT B3 ROUTER IDENTIFICATION REDUCES TO AT MOST TWO
ADDITIONAL BOUNDARY-MEMBERSHIP QUERIES.
```

Once their yes/no answers are known, E101 constructs the explicit constant-size
binary representation or recognizes EQ3 immediately.

This is a useful constructive reduction, but not yet a polynomial algorithm:
those one or two membership queries are themselves exact internal feasibility
questions, and no universal polynomial method for them is proved.

## 14. Correct next target — E103

The old E102 goal

```text
rigid-free => coherent double rectangle
```

is now replaced by a more precise sequence.

### E103-A — signed phase-clash geometry killer

Attack the three minimal two-check holonomy obstructions

```text
H_a^0 versus H_a^1.
```

Use:

```text
* C4-freeness/source linearity;
* cubic degree;
* fixed support parity of a variable;
* the E101 contraction of inert B3 neighborhoods;
* minimality of the chosen six TARGET6 witnesses.
```

Goal:

```text
prove such opposite phases cannot lie in one nonzero-color component,
or construct the first genuine exact TARGET6 source realizing one.
```

### E103-B — higher holonomy

If all size-2 clashes die, attack the 22 minimal size-3 signature families,
then the unique size-4 family.

### E103-C — router membership queries

Either answer the at-most-two B3 boundary queries in polynomial time, or
derive an elimination rule that avoids asking them.

Scientific status:

```text
E102 = COMPLETE FOUR-CANDIDATE LOCAL SIGNATURE CLASSIFICATION
       + E96 GLOBAL-CONSEQUENCE CORRECTION
       + COMPONENT-WISE HOLONOMY LOCALIZATION
       + TWO-QUERY B3 IDENTIFICATION REDUCTION.

E96_LOCAL_31_DEFECT_CLASSIFICATION = VALID.
E96_GLOBAL_THREE_CONFLICT_NECESSITY = SUPERSEDED / WITHDRAWN.
E98_DOUBLE_RECTANGLE_SUFFICIENCY = VALID.
RIGID_FREE_BAD_HOLONOMY_COMPONENT = CURRENT FRONTIER.
CONSTRUCTIVE_ROUTER_MEMBERSHIP_QUERIES = OPEN.
P_VS_NP = OPEN.
```
