# R5 E72 — E12 Multi-Field Rank Middle-Band Firewall

Date: 2026-10-05

Status:
`E12_HARDNESS_IMAGE_HAS_LINEAR_Q_NULLITY_AND_LINEAR_F2_F3_RANK_NULLITY_MARGINS__RANK_MAGNITUDE_DICHOTOMY_FIREWALLED`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

IT SHOWS THAT THE ENTIRE R5 E12 RXC3 HARDNESS IMAGE ALREADY LIES LINEARLY DEEP
INSIDE THE SIMULTANEOUS Q/F2/F3 RANK-NULLITY MIDDLE BAND.

THEREFORE A SECOND IMPLICATION OF THE FORM

    "ALL RELEVANT RANKS/NULLITIES ARE LARGE => EASY STRUCTURAL DECOMPOSITION"

CANNOT BE JUSTIFIED AS AN EASY SIDE CONDITION SEPARATE FROM THE HARD CORE.
IF SUCH AN IMPLICATION IS TRUE UNIVERSALLY, ITS PROOF MUST ACT INSIDE THE E12
NP-HARD IMAGE ITSELF AND WOULD CONSTITUTE THE KIND OF BREAKTHROUGH WE ACTUALLY
SEEK.

P_VS_NP = OPEN.
```

## 1. Why E72 is the correct anti-loop after E70/E71

E61 supplies the rational-kernel exact algorithm

```text
2^d_Q poly(n),
```

where `d_Q = nullity_Q(A)`.

E70 supplies the binary exact envelope

```text
2^min(r_2,d_2) poly(n).
```

E71 supplies, in particular, the ternary exact envelope

```text
3^min(r_3,d_3) poly(n).
```

A tempting next dichotomy would be:

```text
if all small-parameter routes fail,
then large nullity/rank should force another polynomial decomposition.
```

E72 tests this directly against the E12/RXC3 hardness bridge rather than on
special subclasses.

## 2. Source and target notation

Let `R` be a `q x q` square-cubic-linear RXC3 source incidence matrix:

```text
rows    = source elements,
columns = source triples.
```

Every source element occurs in exactly three source triples and every source
triple has size three.

Apply the R5 E12 linearizing gadget to every source triple.  Let `B` be the
natural target incidence matrix.  E12 has exactly 17 target triples per source
triple and the transformed system remains square, so

```text
N = 17 q,
B in {0,1}^{N x N}.
```

Let `H` be the source 3-uniform hypergraph and `c(H)` its number of connected
components.

For a field `K`, write

```text
r_K(M) = rank_K(M),
d_K(M) = nullity_K(M).
```

## 3. Characteristic not three: E17 quotient survives over Q and F2

R5 E17 proved over the rationals that the one-gadget internal `15 x 17` matrix
has

```text
rank = 13,
nullity = 4,
```

and that the six visible port coordinates

```text
(L1,L2,L3,P1,P2,P3)
```

project to the two-dimensional relation

```text
L1=L2=L3=a,
P1=P2=P3=b.
```

The remaining two dimensions are zero-port local gauge modes.

Exact replay shows that the same quotient holds over `F2` (and over `F5` as a
control):

```text
rank_F2(J_int)=13,
port dimension=2,
zero-port gauge dimension=2.
```

Globally, the source-element boundary equations are precisely

```text
R a = 0,
R b = 0.
```

Therefore for `K=Q` and `K=F2`,

```text
boxed:
d_K(B) = 2q + 2 d_K(R).
```

In particular,

```text
d_Q(B) >= 2q,
d_2(B) >= 2q.
```

For the binary rank,

```text
r_2(B)
 = 17q - [2q + 2(q-r_2(R))]
 = 13q + 2r_2(R),
```

so

```text
boxed:
r_2(B) >= 13q.
```

Hence

```text
boxed:
min(r_2(B),d_2(B)) >= 2q.
```

## 4. Characteristic three changes the local quotient

Over `F3`, the same one-gadget internal matrix drops rank by one:

```text
rank_F3(J_int)=12,
nullity_F3(J_int)=5.
```

The six-port projection now has dimension three, while the zero-port local gauge
remains two-dimensional.

An exact parameterization is

```text
L = (a,b,-a-b),
P = (c,c+a-b,c-a+b).
```

Equivalently, the projected port relation is defined by

```text
L1+L2+L3 = 0,
P1+P2+P3 = 0,
(P2-P1) = (L1-L2).
```

All equations here are over `F3`.

## 5. Position-incidence matrices

For every ordered source triple

```text
(u,v,w),
```

let `M1,M2,M3` be the `q x q` matrices placing a one at the first, second and
third position respectively.  Each source triple contributes one one to each
position matrix and

```text
R = M1 + M2 + M3.
```

Define over `F3`

```text
U = M1-M3,
V = M2-M3.
```

Because `-2=1 mod 3`,

```text
U+V
 = M1+M2-2M3
 = M1+M2+M3
 = R.
```

Thus

```text
boxed:
R=U+V over F3.
```

## 6. Global F3 boundary equations

Let vectors `a,b,c in F3^q` collect the three local port parameters for all
source triples.

The unprimed global boundary equations become

```text
U a + V b = 0.
```

The primed equations are

```text
R c + V(a-b) = 0.
```

Using `Ua+Vb=0` and `R=U+V`,

```text
V(a-b)
 = Va - Vb
 = Va + Ua
 = Ra.
```

Therefore the primed system is simply

```text
R(c+a)=0.
```

Put

```text
k=c+a.
```

Then

```text
k in ker_F3(R).
```

The visible ternary kernel therefore separates into

```text
(a,b) in ker[U V]
```

plus an independent source-kernel variable

```text
k in ker_F3(R).
```

## 7. The oriented-incidence rank

For every source triple `(u,v,w)`, replace it by the two oriented graph edges

```text
w -> u,
w -> v.
```

The resulting ordinary graph has the same connected components as the source
hypergraph `H`.

Up to harmless column ordering/sign conventions, `[U V]` is an oriented vertex-
edge incidence matrix of this graph.

The standard oriented-incidence theorem says that over any field a graph with
`q` vertices and `c(H)` connected components has incidence rank

```text
q-c(H).
```

Hence

```text
nullity([U V])
 = 2q - (q-c(H))
 = q+c(H).
```

Adding

```text
* q+c(H) visible (a,b) dimensions,
* d_3(R) source-kernel dimensions from k,
* 2q zero-port gadget gauges,
```

gives

```text
boxed:
d_3(B)=3q+c(H)+d_3(R).
```

For connected source instances this simplifies to

```text
boxed:
d_3(B)=3q+1+d_3(R).
```

The ternary rank is therefore

```text
r_3(B)
 = 17q-[3q+c(H)+q-r_3(R)]
 = 13q+r_3(R)-c(H).
```

Every nonempty connected source component contributes rank at least one, so

```text
r_3(R)>=c(H).
```

Thus

```text
boxed:
r_3(B)>=13q.
```

Also

```text
boxed:
d_3(B)>=3q.
```

and consequently

```text
boxed:
min(r_3(B),d_3(B))>=3q.
```

## 8. Linear-depth multi-field middle band

Recall `N=17q`.  Combining the exact formulas gives the universal E12-image
bounds

```text
boxed:
d_Q(B) >= 2N/17,

boxed:
min(r_2(B),d_2(B)) >= 2N/17,

boxed:
min(r_3(B),d_3(B)) >= 3N/17.
```

So the entire E12 image is not merely outside `O(log N)` easy regimes.  It lies
at **linear distance** from every current rank/nullity edge.

Therefore the existing exact envelopes evaluate to exponential worst-case bounds
on the E12 image:

```text
E61:  2^d_Q              >= 2^(2N/17),
E70:  2^min(r_2,d_2)     >= 2^(2N/17),
E71:  3^min(r_3,d_3)     >= 3^(3N/17),
```

when read purely through those parameters.

These are lower bounds on the **parameterized envelope sizes**, not lower bounds
on the true computational complexity of the instances.

## 9. Frozen replay controls

Companion checker:

```text
experiments/r5_e72_e12_multifield_rank_middle_band_firewall.py
```

It verifies the local field quotient and three global fixtures.

### Frozen E12 q=6 benchmark

```text
source:
    q=6,
    c(H)=1,
    d_Q(R)=0,
    d_2(R)=0,
    d_3(R)=1.

target N=102:
    d_Q(B)=12,
    d_2(B)=12,
    d_3(B)=20,
    r_2(B)=90,
    r_3(B)=82.
```

### Connected q=9 control

A frozen simple square-cubic-linear source has

```text
d_Q(R)=1,
d_2(R)=1,
d_3(R)=2,
c(H)=1.
```

The formulas predict and replay verifies

```text
N=153,
d_Q(B)=20,
d_2(B)=20,
d_3(B)=30,
r_2(B)=133,
r_3(B)=123.
```

### Disconnected two-copy q=12 control

The disjoint union of two frozen q=6 sources has

```text
c(H)=2,
d_3(R)=2.
```

The ternary formula predicts

```text
d_3(B)=3*12+2+2=40,
```

and exact replay verifies it.  This control prevents silently replacing the
component term `c(H)` by a connected-only constant one.

## 10. External anti-loop

The source hard problem is Restricted Exact Cover by 3-Sets (RX3C / RXC3), in
which every element occurs in exactly three triples.  Its NP-completeness is the
classical restriction used by T. F. Gonzalez:

* Teofilo F. Gonzalez, "Clustering to Minimize the Maximum Intercluster
  Distance", Theoretical Computer Science 38 (1985), 293-306,
  DOI `10.1016/0304-3975(85)90224-5`.

The graph-incidence ingredient used in Section 7 is the standard theorem

```text
rank(oriented incidence matrix) = |V|-number_of_components
```

over an arbitrary field; a spanning-forest proof shows field-independence.

The important project-specific step is not either classical fact alone, but the
exact E12 local quotient that transports them into the target rank formulas.

## 11. What E72 kills and what remains alive

E72 kills the **simple magnitude-only** form of the desired second implication:

```text
large d_Q and large binary/ternary rank/nullity
    => automatically bounded-width / easy decomposition.
```

Those inequalities already hold throughout the E12 hard image.

E72 does **not** rule out a universal polynomial theorem using richer structure.
That is precisely the remaining target.  A successful theorem must distinguish
or compress the E12 image using information beyond the scalar values

```text
d_Q, r_2,d_2,r_3,d_3.
```

The next plausible axes are therefore structural dependencies themselves:

```text
* support geometry of cross-field dependencies;
* Smith/integer relation structure beyond rank counts;
* interaction of F2 top-shell constraints with F3 Boolean subset-sum;
* quotient relations after removing provably local gauge modes;
* canonical dependency algebra that remains polynomially representable even
  when all rank/nullity dimensions are linear.
```

Any E73 proposal must be attacked first on the E12 image, not validated only on
tractable torus/design subclasses.

Scientific status:

```text
P_VS_NP = OPEN.
```
