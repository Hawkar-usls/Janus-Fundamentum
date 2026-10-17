# R5 E9 — Kochen–Specker Theta-Equality Countercarrier

Date: 2026-09-28

Status: `JANUS_DERIVED_SOURCE_VALID_THETA_EQUALITY_COUNTERCARRIER__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS CONSTRUCTS AN EXPLICIT LINEAR / CUBIC / SQUARE POSITIVE EXACT-ONE
INSTANCE THAT IS CLASSICALLY UNSAT BUT HAS LOVASZ THETA VALUE n/3.

THEREFORE

    theta(G)=n/3  =>  alpha(G)=n/3

IS FALSE EVEN INSIDE THE JANUS LINEAR-CUBIC CONFLICT-GRAPH CARRIER.

THIS CLOSES LOVASZ-THETA / HOFFMAN-EQUALITY AS A UNIVERSAL EXACT TERMINAL.
IT DOES NOT RULE OUT STRONGER SDPs OR OTHER POLYNOMIAL REPRESENTATIONS.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

External source:
- Mladen Pavicic et al., *Hypergraph Contextuality*, Entropy 21 (2019), 1107.
- The paper records the full-scale Peres `57-40` real 3-dimensional Kochen–Specker set and gives the MMP hypergraph string used below.  Its 40 edges are complete orthogonal triples and it is KS-uncolourable.
- DOI: `10.3390/e21111107`.

Parent JANUS artifacts:
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`
- `research/R5_E9_CUBIC_LINEAR_HOFFMAN_COCLIQUE_EQUIVALENCE_2026-09-27_v1.0.md`
- `research/R5_E9_SINGULAR_PRIME_HPERFECT_RELAXATION_GAP_CONTROL_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_kochen_specker_theta_equality_countercarrier.py`

## 1. Frozen Peres 57-40 source

Use the full-context MMP string

```text
123,345,467,789,92A,ABC,CD4,AEF,5GF,HIJ,HKL,H7M,NCO,OPQ,QRL,RST,
TUJ,JPV,VWX,XYR,VZa,Lba,cde,cT1,cfg,FXM,Mhi,ijg,jkl,lme,ehn,nop,
pqj,nrN,gsN,tu9,tlO,tv5,ap1,1MO
```

It has exactly

```text
57 rays,
40 complete orthogonal contexts,
3 rays per context,
```

and distinct contexts intersect in at most one ray.

The source paper identifies this full-scale configuration as a critical
3-dimensional Kochen–Specker set.  Hence there is no Boolean assignment
putting exactly one `1` in every displayed context, while there is a real
rank-one projector assignment `Q_v` such that every context `{u,v,w}` obeys

```text
Q_u Q_v = Q_u Q_w = Q_v Q_w = 0,
Q_u + Q_v + Q_w = I_3.
```

The checker independently verifies the displayed 57-variable positive
Exact-One system is classically UNSAT by exact propagation/backtracking; the
projective realizability is the source-bound published input fact.

The ray-degree census is

```text
degree 1 : 24 rays
degree 2 :  6 rays
degree 3 : 24 rays
degree 4 :  3 rays
```

and the total incidence count is `120`.

## 2. Two equality gadgets with complementary port degrees

We use two linear positive Exact-One gadgets.

### E2 — port degree two

This is the existing JANUS EQ3 regularizer.  Variables `0,1,2` are terminals and
clauses are

```text
(2,5,6)
(1,4,7)
(5,7,9)
(0,3,7)
(4,6,9)
(2,4,8)
(3,8,9)
(0,5,8)
(1,3,6)
```

Terminal degrees are `2,2,2`; all seven other variables have degree three.
Its exact terminal relation is

```text
{000,111}.
```

For projectors, put terminals `0,1,2,9` in colour `Q`, variables `6,7,8` in
colour `R`, and variables `3,4,5` in colour `S`, where

```text
Q+R+S=I_3
```

is any orthogonal rank-one decomposition. Every gadget clause contains one of
`Q,R,S`.

### E1 — port degree one

Use eleven variables with terminals `0,1,2` and clauses

```text
(1,4,5)
(5,7,8)
(5,9,10)
(3,4,9)
(3,8,10)
(0,6,10)
(4,6,8)
(2,3,7)
(6,7,9)
```

The terminal degrees are `1,1,1`; every other variable has degree three.
The gadget is linear.

Exact rational elimination gives, with free coordinates `q=x_9` and `r=x_10`,

```text
x_0=x_1=x_2=x_8=x_9=q,
x_4=x_7=x_10=r,
x_3=x_5=x_6=1-q-r.
```

Therefore on Boolean solutions the terminal projection is exactly

```text
{000,111}.
```

It also has a projector colouring with

```text
Q : {0,1,2,8,9}
R : {4,7,10}
S : {3,5,6},
```

and every clause contains one `Q`, one `R`, one `S`.

Thus both E1 and E2 enforce the same classical/projective terminal equality,
but their terminal occurrence degrees are complementary:

```text
E1 port degree = 1,
E2 port degree = 2.
```

Identifying one E1 port with one E2 port creates a final variable of degree
three and preserves the common projector value.

## 3. Cubic equality network for any 3d occurrences

Take one logical source ray `v` occurring in `d` original contexts.  Triplicate
every source context, so `v` now has exactly `3d` occurrence slots.

Construct an equality tree as follows.

For `d=1`, take one E2 gadget. Its three E2 ports are the three source-occurrence
ports.

For `d>=2`, take

```text
E1 count = d-1,
E2 count = 2d-1.
```

Arrange the E1 gadgets in a path.  Between consecutive E1 gadgets put one E2
connector and identify one terminal of the connector with one terminal of each
adjacent E1.  Every E1 endpoint of the path has two remaining terminal slots;
every internal E1 has one.  Attach one E2 leaf to each such remaining slot by
identifying an E1 port with one E2 port.

Hence every E1 uses all three terminals.  The E2 connector gadgets use two
ports and each E2 leaf uses one.  Counting the still-free E2 terminals gives

```text
(d-2) connector-free ports + 2(d+1) leaf-free ports = 3d
```

(with the same total obtained directly for the small endpoint cases).

Attach these `3d` free E2 terminals bijectively to the `3d` triplicated source
occurrences of ray `v`.

Every final variable now has degree exactly three:

```text
E1--E2 identified connector : 1+2 = 3,
free E2 port + source clause : 2+1 = 3,
gadget auxiliary variable   : 3.
```

Because the equality-network incidence graph is a tree and every gadget is
linear, two internal clauses share at most one final variable. A source clause
uses one occurrence port from three different logical-ray networks, so it
meets any gadget in at most one variable. Distinct triplicated source clauses
use distinct occurrence ports. Hence the whole output is linear.

## 4. Size of the frozen Peres output

The Peres source has `57` rays and total source degree `120`.

Summing the network counts gives

```text
number of E1 gadgets
 = sum_v (d_v-1)
 = 120-57
 = 63,

number of E2 gadgets
 = sum_v (2d_v-1)
 = 240-57
 = 183.
```

Before E1--E2 port identifications the gadget variables number

```text
63*11 + 183*10 = 2523.
```

The equality forests have

```text
3*sum_v(d_v-1)=189
```

E1--E2 identifications, so the final number of variables is

```text
N = 2523-189 = 2334.
```

Internal clauses number

```text
63*9 + 183*9 = 2214.
```

Triplicating the 40 Peres contexts adds `120` source clauses, hence

```text
M = 2214+120 = 2334 = N.
```

The checker constructs this exact carrier and verifies

```text
N=M=2334,
every row degree = 3,
every column degree = 3,
linearity = PASS.
```

The deterministic generated row-list SHA256 is

```text
93ea25de14d8a8b8db6e685fe06277793bc041039376d31263f2510b20863c37
```

under the checker serialization.

## 5. Classical UNSAT preservation

Every E1/E2 gadget has terminal relation `{000,111}`. Connectivity of each
logical-ray equality tree therefore forces all `3d` source occurrence ports of
that ray to have one common Boolean value.

Each triplicated source context requires exactly one of its three logical-ray
values to be one.  Collapsing equal occurrence copies therefore maps any output
Exact-One witness to a Boolean one-per-context colouring of the original Peres
57-40 KS source.

The latter has none. Hence the 2334_3 carrier is Exact-One UNSAT.

Equivalently, by the JANUS conflict-graph bridge,

```text
alpha(G) < N/3 = 778.
```

## 6. Projective realization survives the regularizer

For each Peres ray `v`, retain its published rank-one projector `Q_v`.
Choose any orthogonal rank-one decomposition of its orthogonal complement,

```text
I_3 = Q_v + R_v + S_v.
```

In every E1/E2 gadget of the equality network for ray `v`, assign its variables
according to the Q/R/S colourings in Section 2.  Identified terminals agree
because both are assigned `Q_v`.

For a triplicated source context `{u,v,w}`, the three occurrence terminals are
assigned `Q_u,Q_v,Q_w`, which are exactly the three mutually orthogonal Peres
ray projectors and sum to `I_3`.

Thus every final source/gadget clause is an orthogonal rank-one decomposition
of `I_3`.

Let `P_j` be the resulting rank-one projector for final variable `j`.
Every final variable belongs to exactly three clauses. Summing

```text
sum_{j in clause} P_j = I_3
```

over all `N` clauses counts every `P_j` three times, so

\[
\boxed{\sum_j P_j=(N/3)I_3.}
\]

## 7. Lovasz theta certificate

Let `G` be the conflict graph of the final linear cubic carrier and define

\[
X_{ij}=\frac1N\operatorname{Tr}(P_iP_j).
\]

This is a Gram matrix in Hilbert--Schmidt space, hence `X >= 0`.
If `ij` is a conflict edge, the two projectors occur in one orthogonal source
triple, so `Tr(P_iP_j)=0`. Also

\[
\operatorname{Tr}X
 = \frac1N\sum_i\operatorname{Tr}(P_i^2)
 = 1.
\]

Therefore `X` is feasible for the standard Lovasz-theta primal SDP. Its
objective is

\[
\begin{aligned}
J\bullet X
&=\frac1N\operatorname{Tr}\left(\left(\sum_iP_i\right)^2\right)\\
&=\frac1N\operatorname{Tr}\left(((N/3)I_3)^2\right)\\
&=N/3.
\end{aligned}
\]

Hence

```text
theta(G) >= N/3.
```

For every JANUS linear cubic conflict graph,

```text
A^T A = 3I+G,
```

so the least eigenvalue is at least `-3`.  The Hoffman/Lovasz spectral bound
therefore gives

```text
theta(G) <= N/3.
```

Thus

\[
\boxed{\vartheta(G)=N/3=778.}
\]

But Section 5 gives

\[
\boxed{\alpha(G)<778.}
\]

This is the required source-valid theta-equality countercarrier.

## 8. Consequence

Freeze:

```text
THETA_EQUALS_HOFFMAN_TARGET
=> CLASSICAL HOFFMAN COCLIQUE
= FALSE EVEN ON LINEAR-CUBIC SOURCE CARRIER.

LOVASZ THETA < n/3
= VALID POLYNOMIAL UNSAT TERMINAL WHEN IT OCCURS.

LOVASZ THETA = n/3
= NOT A SAT CERTIFICATE.
```

The numerical success of theta on small singular-prime UNSAT controls is a
useful preprocessing phenomenon, not a universal theorem.

## 9. Ceiling

```text
PORT-DEGREE-1 EQ3 GADGET E1
= EXACT CLASSICAL EQ3 + PROJECTOR-PRESERVING

PORT-DEGREE-2 EQ3 GADGET E2
= EXISTING JANUS EXACT EQ3 + PROJECTOR-PRESERVING

PERES 57-40 KS SOURCE
= PUBLISHED REAL 3D KS SET

REGULARIZED OUTPUT
= LINEAR / 3-UNIFORM / 3-REGULAR / SQUARE
= 2334_3

CLASSICAL EXACT-ONE
= UNSAT

PROJECTIVE CONTEXT REALIZATION
= YES

CONFLICT GRAPH
alpha(G) < 778
theta(G) = 778

THETA-EQUALITY UNIVERSAL DECIDER
= FALSIFIED

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
